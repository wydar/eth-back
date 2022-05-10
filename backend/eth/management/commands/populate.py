import datetime
import random

from django.core.management.base import BaseCommand
from eth.models import Station

from backend.settings import w3


class Command(BaseCommand):
    help = 'Populate contract with dummy data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'),
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'{int(options["date"].timestamp())}'))
        timestamp = int(options["date"].timestamp())
        stations = Station.objects.all()
        for station in stations:
            contract = w3.eth.contract(address=station.contract_address, abi=station.contract_abi)
            self.stdout.write(self.style.HTTP_INFO(f'---Station {station.pk}'))
            # contract.functions.addMeassure(msg['Temperature'],msg['Pressure'],msg['Approx-Altitude'],msg['Humidity'],msg['Timestamp']).transact()
            for x in range(0, 1440):
                contract.functions.addMeassure(getRandom(20, 25), getRandom(0, 1), 10722,
                                               getRandom(40, 60), timestamp).transact()
                timestamp += 60
            self.stdout.write(self.style.SUCCESS(f'---Station {station.pk} Done!'))
        self.stdout.write(self.style.SUCCESS('DONE!'))


def getRandom(value1, value2):
    return int(round(random.uniform(value1, value2), 2)*100)
