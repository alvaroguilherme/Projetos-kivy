from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from datacards import CardInputRegister, CardHoldingRegister, CardCoil
from kivy.core.window import Window
from pyModbusTCP.client import ModbusClient
from kivymd.uix.snackbar import Snackbar
from kivy.clock import Clock

class MyWidget(MDScreen):
    def __init__(self, tags, **kwargs):
        super().__init__(**kwargs)
        self._tags = tags
        self._modbusClient = ModbusClient()
        for tag in self._tags:
            if tag['type'] == 'input':
                self.ids.modbus_data.add_widget(CardInputRegister(tag,self._modbusClient))
            elif tag['type'] == 'holding':
                self.ids.modbus_data.add_widget(CardHoldingRegister(tag,self._modbusClient))
            elif tag['type'] == 'coil':
                self.ids.modbus_data.add_widget(CardCoil(tag,self._modbusClient))
    
    def connect(self):
        if self.ids.bt_con.text == 'CONECTAR':
            self.ids.bt_con.text = 'DESCONECTAR'
            self.ids.bt_con.icon = 'power-plug-off'
            try:
                self._modbusClient.host = self.ids.hostname.text
                self._modbusClient.port = int(self.ids.port.text)
                self._modbusClient.open()
                Snackbar(text='Conexão realizada com sucesso!',bg_color=(0,1,0,0.7)).open()
                self._ev = []
                for card in self.ids.modbus_data.children:
                    if card.tag['type'] == 'holding' or card.tag['type'] == 'coil':
                        self._ev.append(Clock.schedule_once(card.update_data))
                    else:
                        self._ev.append(Clock.schedule_interval(card.update_data,1))

            except Exception as e:
                print('Erro: ',e.args)
        
        else:
            self.ids.bt_con.text = 'CONECTAR'
            self.ids.bt_con.icon = 'connection'
            for event in self._ev:
                event.cancel()
            self._modbusClient.close()
            Snackbar(text='Cliente desconectado!',bg_color=(1,0,0,1)).open()


class BasicApp(MDApp):
    __tags = [
        {'name':'tempForno','description':'Temperatura Forno','unit':'ºC','address':1000,'type':'input'},
        {'name':'setpoint','description':'Temperatura Desejada','unit':'ºC','address':2000,'type':'holding'},
        {'name':'status','description':'Estado do Atuador','address':1000,'type':'coil'}
    ]
    def build(self):
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.primary_hue = '500'
        self.theme_cls.accent_palette = 'Blue'
        return MyWidget(self.__tags)

if __name__ == '__main__':
    Window.size = (800,600)
    Window.fullscreen = False
    BasicApp().run()