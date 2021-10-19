import json

STATUS_NEW = 0
STATUS_PENDING = 99
STATUS_CANCELLED = 4
STATUS_COMPLETED = 2
STATUS_PARTIAL = 1
STATUS_REJECTED = 8
STATUS_REPLACED = 6
STATUS_NOT_REPLACED = 9
STATUS_NOT_CANCELLED = 10

EXEC_TYPE_NEW = "0"
EXEC_TYPE_REPLACE = "5"
EXEC_TYPE_INFO = "I"
EXEC_TYPE_TRADE = "F"

TYPE_REPORT = "8"
TYPE_TRADE = "F"
TYPE_ORDER = "D"
TYPE_INFO_TRADE = "AE"

TYPE_CANCEL_ORDER = "F"
TYPE_REPLACE_ORDER = "G"

SIDE_COMPRA = 0
SIDE_VENTA = 1


class Report(object):
    attrs = {
        "type": {"data_type": str, "required": True, "values": [TYPE_REPORT,
                                                                TYPE_TRADE,
                                                                TYPE_INFO_TRADE]},
        "exchange": {"data_type": str, "required": True, "default": ""},
        "book": {"data_type": str, "required": False,"default":""},
        "crypto": {"data_type": str, "required": True},
        "currency": {"data_type": str, "required": True},
        "side": {"data_type": int, "required": True, "values": [0, 1]},
        "order_id": {"data_type": str, "required": False, "default": ""},
        "qty": {"data_type": float, "required": False, "default": 0},
        "last_qty": {"data_type": float, "required": False, "default": 0},
        "leaves_qty": {"data_type": float, "required": False, "default": 0},
        "cum_qty": {"data_type": float, "required": False, "default": 0},
        "price": {"data_type": float, "required": False, "default": 0},
        "last_price": {"data_type": float, "required": False, "default": 0},
        "client_id": {"data_type": str, "required": False, "default": ""},
        "status": {"data_type": int, "required": True, "values": [STATUS_NEW,
                                                                   STATUS_PENDING,
                                                                   STATUS_CANCELLED,
                                                                   STATUS_COMPLETED,
                                                                   STATUS_PARTIAL,
                                                                   STATUS_REJECTED,
                                                                   STATUS_REPLACED,
                                                                   STATUS_NOT_REPLACED,
                                                                   STATUS_NOT_CANCELLED], "default": STATUS_NEW},
        "exec_type": {"data_type": str, "required": False, "values": [EXEC_TYPE_NEW,
                                                                      EXEC_TYPE_REPLACE,
                                                                      EXEC_TYPE_INFO,
                                                                      EXEC_TYPE_TRADE],
                      "default": EXEC_TYPE_NEW},
        "order_type": {"data_type": str, "required": False, "default": "limit"},
        "time_in_force": {"data_type": str, "required": False, "default": "goodtillcancelled"},
        "trader_id": {"data_type": str, "required": False, "default": ""},
        "fees_currency": {"data_type": str, "required": False, "default": ""},
        "fees_qty": {"data_type": float, "required": False, "default": 0},
        "stop_price": {"data_type": float, "required": False, "default": 0},
        "status_text": {"data_type": str, "required": False, "default": ""},
        "account": {"data_type": str, "required": False, "default": ""},
        "oid_maker": {"data_type": str, "required": False, "default": ""},
        "oid_taker": {"data_type": str, "required": False, "default": ""},
        "text": {"data_type": str, "required": False, "default": ""},
        "code_error": {"data_type": str, "required": False, "default": ""},
        "trade_id": {"data_type": int, "required": False, "default": 0},
        "datetime": {"data_type": float, "required": False, "default": 0},
    }

    def __init__(self, *args, ** kwargs):
        '''
            Report("{JSON string}"),
            Report({JSON object}"),
            Report(key=value),
            Report(JSON, key=value),
        '''
        self.inst_attrs = {}
        json_data = {}
        try:
            if isinstance(args[0], str):
                json_data = json.loads(args[0])
            else:
                json_data = args[0]
        except (LookupError, TypeError) as e:
            json_data = {}
        except Exception as e:
            print(e)
            raise Exception(e)

        for key in self.attrs:
            
            value = json_data.get(key)           
            if value is None : value = kwargs.get(key)
            if value is None and self.attrs[key].get('required'):
                raise KeyError(f"El atributo '{key}' es obligatorio | {value}")
            else:                
                try:
                    self.set_value(key, value)
                except ValueError:
                    try:
                        self.set_value(key, kwargs.get(key))
                    except ValueError:
                        self.set_value(key, self.attrs[key].get('default'))        

    def get_value(self, key): return self.inst_attrs.get(key)

    def set_value(self, key, val):
        if val is None: raise ValueError(f"{key} = {val}")
        if not isinstance(val, self.attrs[key].get('data_type')):
            try:
                if self.attrs[key]['data_type'] in ( int, float) and val=="": val = 0                
                val = self.attrs[key]['data_type'](val)
            except:
                raise TypeError(
                    f"El atributo '{key}' debe ser un {self.attrs[key]['data_type']}")
        
        if self.attrs[key].get('values') is not None and val not in self.attrs[key].get('values'):
            raise ValueError(
                f"El atributo '{key}' debe ser uno de {self.attrs[key].get('values')}")
        
        self.inst_attrs[key] = val

    def to_json(self):
        return self.inst_attrs

    def __repr__(self):
        return json.dumps(self.inst_attrs)

    def __hash__(self):
        ''' Se usa para buscar mas rapidamente en los diccionarios '''
        return f"{self.inst_attrs['type']}_{self.inst_attrs['order_id']}_{self.inst_attrs['book']}_{self.inst_attrs['status']}"

    def __eq__(self, other):
        if self.__hash__() == other.__hash__():
            return True
        return False


class Orden(Report):
    attrs = {
        "exchange": {"data_type": str, "required": True, "default": ""},
        "type": {"data_type": str, "required": False, "values": [TYPE_ORDER, TYPE_CANCEL_ORDER, TYPE_REPLACE_ORDER], "default": TYPE_ORDER},
        "order_id": {"data_type": str, "required": False, "default": ""},
        "book": {"data_type": str, "required": False, "default": ""},
        "crypto": {"data_type": str, "required": False, "default": ""},
        "currency": {"data_type": str, "required": False, "default": ""},
        "side": {"data_type": int, "required": False, "values": [SIDE_COMPRA, SIDE_VENTA], "default": SIDE_COMPRA},
        "qty": {"data_type": float, "required": False, "default": 0},
        "price": {"data_type": float, "required": False, "default": 0},
        "time_in_force": {"data_type": str, "required": False, "default": "goodtillcancelled"},
        "datetime": {"data_type": int, "required": False, "default": 0},
        "stop_price": {"data_type": float, "required": False, "default": 0},
        "client_id": {"data_type": str, "required": False, "default": ""},
        "order_type": {"data_type": str, "required": False, "default": "limit"},
    }

    def __hash__(self):
        return self.get_value('order_id')

    def __eq__(self, other):
        try:
            return self.__hash__() == other.__hash__()
        except:
            return False

    def __ne__(self, other):
        try:
            return self.__hash__() != other.__hash__()
        except:
            return False

    def __lt__(self, other):
        try:
            if self.get_value('side') == 0:
                return (self.get_value('price'), self.get_value('datetime')) > (other.get_value('price'), other.get_value('datetime'))
            else:
                return (self.get_value('price'), self.get_value('datetime')) < (other.get_value('price'), other.get_value('datetime'))
        except:
            return False

    def __gt__(self, other):
        try:
            if self.get_value('side') == 0:
                return (self.get_value('price'), self.get_value('datetime')) < (other.get_value('price'), other.get_value('datetime'))
            else:
                return (self.get_value('price'), self.get_value('datetime')) > (other.get_value('price'), other.get_value('datetime'))
        except:
            return False

    def __ge__(self, other):
        if self.__lt__(other):
            return False
        return True

    def __le__(self, other):
        if self.__gt__(other):
            return False
        return True

if __name__ == "__main__":
    order = {"exchange":"hh","price": 1979.36, "qty": 5.82883672, "order_id": "olanAlD1Lsd7Gimt",
             "side": 0, "amount": "11537.36625009", "datetime": 1626199829374}
    order = {'book': 'btc_ars', 'side': 1, 'cryto': 'btc', 'exchange': 'Bitso', 'currency': 'ars', 'type': 'limit', 'qty': '0.0001','price': '321', 'stop': '', 'time_in_force': 'goodtillcancelled', 'client_id': 'MN_42hDw2KwEv29po7vR'}
    order = {"exchange": "Bitso", "type": "D", "order_id": "", "book": "btc_ars", "crypto": "btc", "currency": "ars", "side": 0, "qty": 0.0015,
             "price": 5725275.0, "time_in_force": "goodtillcancelled", "datetime": 0, "stop_price": 0.0, "client_id": "MN_3JfmDqGbHuUMjHH62", "order_type": "limit"}
    order = {'o': 'aCf9QL8ETo4gyQZ0', 'd': 1626381900275, 'r': '5469351.81', 't': 0, 'a': '0.0323821', 'v': '177109.0972466', 's': 'open'}
    o = Report(type=8, exchange='Bitso', book="kkj",crypto='dd',currency='s', price=float(order['r']), qty=float(order['a']),
                                order_id=order['o'], side=order['t'], datetime=order['d'])
    
    print(o)
