from twisted.protocols import basic
from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
from serial import PARITY_EVEN, SEVENBITS
from houseagent.plugins import pluginapi
import ConfigParser
import os
import traceback

class SmartMeterReadings(object):
    '''
    This class represents smartmeter readings.
    '''
    
    def __init__(self, low_tariff, normal_tariff, low_tariff_produced, normal_tariff_produced, actual_usage, gas_usage):
        self.low_tariff = low_tariff
        self.normal_tariff = normal_tariff
        self.low_tariff_produced = low_tariff_produced
        self.normal_tariff_produced = normal_tariff_produced
        self.actual_usage = actual_usage
        self.gas_usage = gas_usage
        

    def __repr__(self):
        return '[SmartMeterReadings] Low tariff: %7.3fkWh, normal tariff: %7.3fkWh, low tariff produced: %7.3fkWh, ' \
               'normal tariff produced: %7.3fkWh, actual usage: %rW, gas usage: %7.3fM3' % (self.low_tariff, self.normal_tariff, 
                                                                                            self.low_tariff_produced, 
                                                                                            self.normal_tariff_produced, 
                                                                                            self.actual_usage, self.gas_usage)

    
class SmartMeterProtocol(basic.LineReceiver):
    '''
    This class handles the smartmeter protocol.
    '''
    
    def __init__(self, wrapper):
        self._wrapper = wrapper
        self._telegram = []
        
    
    def connectionMade(self):
        for connection in self._wrapper.connections:
            connection.ready()
        

    def lineReceived(self, line):
        
        if line.startswith('!'):
            try:
                readings = self._parse_telegram(self._telegram)
            
                values = {'Energy usage normal tariff (kWh)': readings.normal_tariff, 
                          'Energy usage low tariff (kWh)': readings.low_tariff,
                          'Actual energy usage (W)': readings.actual_usage,
                          'Total gas usage (M3)': readings.gas_usage}
                
                print readings
                
                for connection in self._wrapper.connections:
                    connection.value_update(1, values)                     
                
                self._telegram = []

            except Exception, exp:
                print traceback.format_exc()

        else:
            self._telegram.append(line)
            
            
    def _parse_telegram(self, telegram):
        '''
        This function parses a B101 smartmeter telegram.
        More information about this telegram can be found here: 
        http://www.energiened.nl/_upload/bestellingen/publicaties/284_P1Smart%20Meter%20v2.1%20final%20P1.pdf
        
        @param telegram: the telegram to parse
        '''
        
        low_tariff = 0
        normal_tariff = 0
        low_tariff_produced = 0
        normal_tariff_produced = 0
        actual_usage = 0
        gas_usage = 0
        next_is_gas = False
        
        for tg in telegram:
            print tg
            if tg.startswith('1-0:1.8.1'):
                low_tariff = float(tg[tg.index('(')+1:tg.index('*')])
            if tg.startswith('1-0:1.8.2'):
                normal_tariff = float(tg[tg.index('(')+1:tg.index('*')])
            if tg.startswith('1-0:2.8.1'):
                low_tariff_produced = float(tg[tg.index('(')+1:tg.index('*')])
            if tg.startswith('1-0:2.8.2'):
                normal_tariff_produced = float(tg[tg.index('(')+1:tg.index('*')])
            if tg.startswith('1-0:1.7.0'):
                actual_usage = float(tg[tg.index('(')+1:tg.index('*')]) * 1000.0

            if next_is_gas and tg.startswith('('):
                gas_usage = float(tg[tg.index('(')+1:tg.index(')')])
            next_is_gas = False
            if tg.startswith('0-1:24.3.0'):
                next_is_gas = True
        
        return SmartMeterReadings(low_tariff, normal_tariff, low_tariff_produced, normal_tariff_produced, actual_usage, gas_usage)

            
class SmartMeterWrapper(object):
    '''
    This wrapper class glues the protocl and broker connections together.
    '''
    
    def __init__(self):
        
        self._brokers = {}
        self.connections = []
        self._read_configuration()

        callbacks = {}
        
        for key, broker_info in self._brokers:
            broker_info = broker_info.split(';')
            
            self.connections.append( pluginapi.PluginAPI(broker_info[2], 'SmartMeter', 
                                             broker_host=broker_info[0], 
                                             broker_port=int(broker_info[1]), **callbacks) )
        
        SerialPort (SmartMeterProtocol(self), self._serial, reactor, bytesize=SEVENBITS, parity=PARITY_EVEN)
        
        reactor.run()
        
        
    def _read_configuration(self):
        '''
        Parse configuration from the smartmeter.conf configuration file.
        '''
        
        config_file = 'smartmeter.conf'
        
        config = ConfigParser.RawConfigParser()
        if os.path.exists(config_file):
            config.read(config_file)
        else:
            config.read('smartmeter.conf')
            
        self._brokers = config.items('brokers')
        self._serial = config.get('serial', 'port')
        
        
if __name__ == '__main__':
    sm_wrap = SmartMeterWrapper()