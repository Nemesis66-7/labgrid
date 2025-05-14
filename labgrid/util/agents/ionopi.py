"""
This module implements switching GPIOs via Ionopi sysfs GPIO interface.

"""
import logging
import os
import os.path
from time import sleep

log = logging.getLogger(__name__)

class Ionopi:
    _ionopi_path_prefix = '/sys/class/ionopi/'
    _max_adc_count = 4
    _max_relay_count = 2
    _max_digital_in_count = 6
    _max_oc_count = 3

    @staticmethod
    def assert_ionopi():
        if not os.path.isdir(Ionopi._ionopi_path_prefix):
            raise ValueError("Ionopi syspath not found or is not a directory")

    @staticmethod
    def get_relay_sysfs_path(index):
        Ionopi.assert_ionopi()

        if index <= 0 or index > Ionopi._max_relay_count:
            raise ValueError(f"Ionopi relay index {index} out of range.")

        relay_sysfs_path = os.path.join(Ionopi._ionopi_path_prefix,
                                        f'relay/o{index}')
        if not os.path.isfile(relay_sysfs_path):
            raise ValueError(f"Ionopi relay file not found {relay_sysfs_path}")
        return relay_sysfs_path

    @staticmethod
    def get_adc_sysfs_path(index):
        Ionopi.assert_ionopi()

        if index <= 0 or index > Ionopi._max_adc_count:
            raise ValueError(f"Ionopi adc index {index} out of range")

        adc_sysfs_path = os.path.join(Ionopi._ionopi_path_prefix,
                                      f'analog_in/ai{index}_mv')
        if not os.path.isfile(adc_sysfs_path):
            raise ValueError(f"Ionopi adc file not found {adc_sysfs_path}")
        return adc_sysfs_path

    @staticmethod
    def get_digital_in_sysfs_path(index, type="deb"):
        Ionopi.assert_ionopi()

        if index <= 0 or index > Ionopi._max_digital_in_count:
            raise ValueError(f"Ionopi digital in index {index} out of range.")

        if type not in ["deb", "deb_on_ms", "deb_off_ms", "deb_on_cnt", "deb_off_cnt"]:
            raise ValueError(f"Ionopi digital in type {type} out of range.")

        digital_in_sysfs_path = os.path.join(Ionopi._ionopi_path_prefix,
                                             f'digital_in/di{index}_{type}')
        if not os.path.isfile(digital_in_sysfs_path):
            raise ValueError(f"Ionopi digital in file not found {digital_in_sysfs_path}")
        return digital_in_sysfs_path

    @staticmethod
    def get_led_sysfs_path(type="status"):
        Ionopi.assert_ionopi()

        if type not in ["status", "blink"]:
            raise ValueError(f"Ionopi led type {type} out of range.")

        led_sysfs_path = os.path.join(Ionopi._ionopi_path_prefix,
                                      f'led/{type}')
        if not os.path.isfile(led_sysfs_path):
            raise ValueError(f"Ionopi led file not found {led_sysfs_path}")
        return led_sysfs_path

    @staticmethod
    def get_oc_sysfs_path(index):
        Ionopi.assert_ionopi()

        if index <= 0 or index > Ionopi._max_oc_count:
            raise ValueError(f"Ionopi ic index {index} out of range.")

        oc_sysfs_path = os.path.join(Ionopi._ionopi_path_prefix,
                                     f'open_coll/oc{index}')
        if not os.path.isfile(oc_sysfs_path):
            raise ValueError(f"Ionopi oc file not found {oc_sysfs_path}")
        return oc_sysfs_path

    @staticmethod
    def get_relay(index):
        with open(Ionopi.get_relay_sysfs_path(index), "r") as fd:
            literal_value = fd.read(1)
            print(literal_value)
            if literal_value == '0':
                return False
            elif literal_value == '1':
                return True
            raise ValueError("relay value is out of range.")

    @staticmethod
    def set_relay(index, status):
        with open(Ionopi.get_relay_sysfs_path(index), "w") as fd:
            written_bytes = fd.write('1' if status else '0')
            if written_bytes != 1:
                raise ValueError("relay failed to write.")

    @staticmethod
    def get_adc_mv(index):
        with open(Ionopi.get_adc_sysfs_path(index), "r") as fd:
            literal_value = fd.read()
            return int(literal_value)

    @staticmethod
    def configure_digital_in(index, debounce_on_ms, debounce_off_ms):
        with open(Ionopi.get_digital_in_sysfs_path(index, "deb_on_ms"), "w") as fd:
            written_bytes = fd.write(str(debounce_on_ms))
            if written_bytes <= 0:
                raise ValueError("digital in on debounce failed to write.")

        with open(Ionopi.get_digital_in_sysfs_path(index, "deb_off_ms"), "w") as fd:
            written_bytes = fd.write(str(debounce_off_ms))
            if written_bytes <= 0:
                raise ValueError("digital in off debounce failed to write.")

    @staticmethod
    def get_digital_in(index):
        with open(Ionopi.get_digital_in_sysfs_path(index), "r") as fd:
            literal_value = fd.read()
            return int(literal_value)

    @staticmethod
    def get_digital_in_on_count(index):
        with open(Ionopi.get_digital_in_sysfs_path(index, "deb_on_cnt"), "r") as fd:
            literal_value = fd.read()
            return int(literal_value)

    @staticmethod
    def get_digital_in_off_count(index):
        with open(Ionopi.get_digital_in_sysfs_path(index, "deb_off_cnt"), "r") as fd:
            literal_value = fd.read()
            return int(literal_value)

    @staticmethod
    def set_led(status):
        with open(Ionopi.get_led_sysfs_path(), "w") as fd:
            written_bytes = fd.write('1' if status else '0')
            if written_bytes != 1:
                raise ValueError("led set failed to write.")

    @staticmethod
    def set_led_blink(on_ms, off_ms=0, rep=0):
        with open(Ionopi.get_led_sysfs_path("blink"), "w") as fd:
            if off_ms == 0 and rep == 0:
                written_bytes = fd.write(f"{on_ms}")
            else:
                written_bytes = fd.write(f"{on_ms} {off_ms} {rep}")
            if written_bytes <= 0:
                raise ValueError("led set failed to write.")

    @staticmethod
    def set_oc(index, status):
        with open(Ionopi.get_oc_sysfs_path(index), "w") as fd:
            written_bytes = fd.write('1' if status else '0')
            if written_bytes != 1:
                raise ValueError("oc set failed to write.")

    @staticmethod
    def get_oc(index):
        with open(Ionopi.get_oc_sysfs_path(index), "r") as fd:
            literal_value = fd.read(1)
            print(literal_value)
            if literal_value == '0':
                return False
            elif literal_value == '1':
                return True
            raise ValueError("oc value is out of range.")

methods = {
    'set_relay':                    Ionopi.set_relay,
    'get_relay':                    Ionopi.get_relay,
    'get_adc_mv':                   Ionopi.get_adc_mv,
    'configure_digital_in':         Ionopi.configure_digital_in,
    'get_digital_in':               Ionopi.get_digital_in,
    'get_digital_in_on_count':      Ionopi.get_digital_in_on_count,
    'get_digital_in_off_count':     Ionopi.get_digital_in_off_count,
    'set_led':                      Ionopi.set_led,
    'set_led_blink':                Ionopi.set_led_blink,
    'set_oc':                       Ionopi.set_oc,
    'get_oc':                       Ionopi.get_oc,
}