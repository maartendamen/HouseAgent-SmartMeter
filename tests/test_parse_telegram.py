import unittest
from smartmeter import SmartMeterProtocol

class Test(unittest.TestCase):

    TELEGRAM =  ['/ISk5\2ME382-1003',
                 '',
                 '0-0:96.1.1(4B414C37303035303632363735323131)', 
                 '1-0:1.8.1(00000.000*kWh)', 
                 '1-0:1.8.2(00003.479*kWh)', 
                 '1-0:2.8.1(00000.000*kWh)', 
                 '1-0:2.8.2(00001.467*kWh)', 
                 '0-0:96.14.0(0002)', 
                 '1-0:1.7.0(0000.29*kW)', 
                 '1-0:2.7.0(0000.00*kW)', 
                 '0-0:17.0.0(0999.00*kW)',
                 '0-0:96.3.10(1)',
                 '0-0:96.13.1()',
                 '0-0:96.13.0()',
                 '0-1:24.1.0(3)',
                 '0-1:96.1.0(3238313031353431313030383337363131)',
                 '0-1:24.3.0(120323170000)(00)(60)(1)(0-1:24.2.1)(m3)',
                 '(00000.437)',
                 '0-1:24.4.0(1)']
    
    def setUp(self):
        self._smartmeter = SmartMeterProtocol()

    def testParseTelegram(self):
        readings = self._smartmeter._parse_telegram(self.TELEGRAM)
        
        self.assertEqual(readings.normal_tariff, 00003.479, 'Unexpected normal tariff result')
        self.assertEqual(readings.low_tariff, 00000.000, 'Unexpected low tariff result')
        self.assertEqual(readings.low_tariff_produced, 00000.000, 'Unexpected low tariff produced result')
        self.assertEqual(readings.normal_tariff_produced, 00001.467, 'Unexpected normal tariff produced result')
        self.assertEqual(readings.actual_usage, 290, 'Unexpected actual usage result')
        self.assertEqual(readings.gas_usage, 00000.437, 'Unexpected gas usage result')
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()