import json
import pandas as pd

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action

from web3 import Web3

from eth.serializers import StationSerializer  # , MeasureSerializer
from eth.models import Station  # , Measures

from backend.settings import BLOCKCHAIN_SERVER, ABI, BYTE_CODE, w3


# class StationViewSet2(viewsets.ModelViewSet):
#     """
#     A simple ViewSet for viewing and editing Stations.
#     """
#     queryset = Station.objects.all()
#     serializer = StationSerializer


# class MeasuresViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
#     """
#     A simple ViewSet for viewing and editing Measures.
#     """
#     queryset = Measures.objects.none()
#     serializers = MeasureSerializer

#     @staticmethod
#     def parseMeasures(station, measures, response):
#         """
#         Function to parse the blockchain response into JSON format
#         """
#         temperatures, altitudes, humidities, preassures, timestamps = measures

#         response_aux = {}
#         num = 0
#         for temp, alt, hum, pre, tim in zip(temperatures, altitudes, humidities, preassures, timestamps):
#             response_aux[num] = {
#                 'temperaure': temp/100,
#                 'altitude': alt/100,
#                 'humidity': hum/100,
#                 'preassure': pre/100,
#                 'timestamp': tim
#                 }
#             num += 1

#         response_aux[station.station_id] = response_aux
#         return json.loads(json.dumps(response))

#     def list(self, request, *args, **kwargs):
#         """
#         Endpoint to connect with the blockchain and retrieve last measure of all stations
#         """
#         stations = Station.objects.filter('is_active'==True)
#         response_data = {}
#         for station in stations:
#             contract = w3.eth.contract(address=station.contract_adress, abi=station.contract_abi)
#             measure = contract.functions.getMeasures(1).call()
#             response_data = MeasuresViewSet.parseMeasures(station, measure, response_data)
#         return Response(data=response_data, status=status.HTTP_200_OK)

#     def station(self, request, *args, **kargs):
#         """
#         Endpoint to connect with the blockchain and retrieve measures of one station
#         """
#         w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_SERVER))
#         w3.eth.defaultAccount = w3.eth.accounts[1]
#         contract = w3.eth.contract(address='', abi=ABI)

#         timestamp = request.GET.get('date')

#         if not timestamp:
#             measure = contract.functions.getMeasures(1).call()
#         else:
#             try:
#                 measure = contract.functions.getLastMeasuresFromTimestamp(int(timestamp)).call()
#             except ValueError:
#                 return Response(data='Bad date format', status=status.HTTP_400_BAD_REQUEST)
#         response_data = MeasuresViewSet.parseMeasures(measure)
#         return Response(data=response_data, status=status.HTTP_200_OK)


class StationViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    @staticmethod
    def parseMeasures(station, measures):
        """
        Function to parse the blockchain response into JSON format
        """
        temperatures = measures[0]
        altitudes = measures[1]
        humidities = measures[2]
        preassures = measures[3]
        timestamps = measures[4]

        response_aux = {}
        num = 0
        for temp, alt, hum, pre, tim in zip(temperatures, altitudes, humidities, preassures, timestamps):
            response_aux[num] = {
                'temperaure': temp/100,
                'altitude': alt/100,
                'humidity': hum/100,
                'preassure': pre/100,
                'timestamp': tim
                }
            num += 1

        # response_aux[station.station_id] = response_aux
        return response_aux.copy()

    @staticmethod
    def groupData(data):
        df = pd.DataFrame(data).T
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df = df.resample("H", on='timestamp').sum() / 60
        df = df.reset_index(level=0)
        return df.T.to_json()

    @action(detail=False, methods=['post'])
    def deploy(self, request):
        """
        Endpoint to deploy a new contract in the Blockcahin
        ---------------------------------------------------

        Example body:

        {
            "id":id,
            "name":name,
            "latitude": latitude,
            "longitude": longitude
        }
        """

        js = json.loads(request.body)

        if not Station.objects.filter(pk=js['id']).exists():
            instance = Station()
            instance.pk = str(js['id'])
            instance.save()

            tx_hash = w3.eth.contract(
                abi=ABI,
                bytecode=BYTE_CODE
            ).constructor().transact()

            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

            contract = w3.eth.contract(address=tx_receipt.contractAddress, abi=ABI)
            contract.functions.setStationValue(js['name'], js['latitude'], js['longitude'], js['id']).transact()

            instance.contract_address = tx_receipt.contractAddress
            instance.contract_abi = ABI
            instance.contract_byte_code = BYTE_CODE
            instance.save()
            return Response(data={"address": tx_receipt.contractAddress}, status=status.HTTP_200_OK)
        else:
            return Response(data={'error': 'station with id {0} already exists'.format(js['id'])})

    @action(detail=False, methods=['get'])
    def measures(self, request, *args, **kwargs):
        """
        Endpoint to connect with the blockchain and retrieve last measure of all stations
        """
        stations = Station.objects.filter(is_active=True)
        response_data = {}
        for station in stations:
            print(stations)
            contract = w3.eth.contract(address=station.contract_address, abi=station.contract_abi)
            measure = contract.functions.getMeasures(1).call()
            response_data[station.station_id] = StationViewSet.parseMeasures(station, measure)
        return Response(data=[response_data], status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def stationmeasures(self, request, *args, **kwargs):
        """
        Endpoint to connect with the blockchain and retrieve measures of one station
        """
        w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_SERVER))
        w3.eth.defaultAccount = w3.eth.accounts[1]
        station = Station.objects.get(pk=kwargs['pk'])
        contract = w3.eth.contract(address=station.contract_address, abi=station.contract_abi)

        timestamp = request.GET.get('date')

        if not timestamp:
            measure = contract.functions.getMeasures(1).call()
            response_data = StationViewSet.parseMeasures(station, measure)
            print(measure)
        else:
            try:
                measure = contract.functions.getLastMeasuresFromTimestamp(int(timestamp)).call()
                response_data = StationViewSet.parseMeasures(station, measure)
                response_data = json.loads(StationViewSet.groupData(response_data))
            except ValueError as e:
                print(e)
                return Response(data='Bad date format', status=status.HTTP_400_BAD_REQUEST)
        return Response(data=response_data, status=status.HTTP_200_OK)
