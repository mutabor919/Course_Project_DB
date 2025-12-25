import os
import subprocess
import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from incidents.models import BackupLog, CustomUser


class Command(BaseCommand):
    help = 'Создает бэкап БД и загружает на Яндекс.Диск'

    def handle(self, *args, **options):
        self.stdout.write("⏳ Начинаем процесс бэкапа...")

        if not os.path.exists(settings.BACKUP_ROOT):
            os.makedirs(settings.BACKUP_ROOT)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"backup_{timestamp}.sql"
        filepath = os.path.join(settings.BACKUP_ROOT, filename)

        db_conf = settings.DATABASES['default']
        env = os.environ.copy()
        env['PGPASSWORD'] = db_conf['PASSWORD']

        command = [
            settings.PG_DUMP_PATH,
            '-h', db_conf['HOST'],
            '-p', db_conf['PORT'],
            '-U', db_conf['USER'],
            '-f', filepath,
            db_conf['NAME']
        ]

        local_success = False
        cloud_success = False
        status_msg = "Ошибка"

        try:
            subprocess.run(command, env=env, check=True)
            self.stdout.write(self.style.SUCCESS(f"✅ Локальный файл создан: {filename}"))
            local_success = True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Ошибка pg_dump: {e}"))
            status_msg = f"Ошибка локально: {e}"

        if local_success:
            self.stdout.write("☁️ Загрузка на Яндекс.Диск...")

            headers = {
                'Authorization': f'OAuth {settings.YANDEX_DISK_TOKEN}'
            }
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            folder_name = "Course_Backups"

            try:
                requests.put(
                    "https://cloud-api.yandex.net/v1/disk/resources",
                    headers=headers,
                    params={'path': folder_name}
                )

                params = {
                    'path': f'{folder_name}/{filename}',
                    'overwrite': 'true'
                }
                resp_link = requests.get(upload_url, headers=headers, params=params)

                if resp_link.status_code == 200:
                    href = resp_link.json().get('href')

                    with open(filepath, 'rb') as f:
                        resp_upload = requests.put(href, files={'file': f})

                    if resp_upload.status_code == 201:
                        self.stdout.write(self.style.SUCCESS("✅ Файл успешно загружен в облако!"))
                        cloud_success = True
                        status_msg = "Успешно (Облако)"
                    else:
                        self.stdout.write(self.style.ERROR(f"Ошибка загрузки: {resp_upload.status_code}"))
                        status_msg = "Ошибка загрузки в облако"
                else:
                    self.stdout.write(self.style.ERROR(f"Ошибка получения ссылки: {resp_link.json()}"))
                    status_msg = "Ошибка API Яндекса"

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Сбой сети: {e}"))
                status_msg = f"Сбой сети: {e}"

        admin_user = CustomUser.objects.filter(role__name='Admin').first()

        BackupLog.objects.create(
            initiator=admin_user,
            file_name=filename,
            status=status_msg,
            file_path=f"YandexDisk:/{folder_name}/{filename}" if cloud_success else filepath
        )