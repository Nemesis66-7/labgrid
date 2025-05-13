import attr
from pexpect import TIMEOUT
import can
import j1939

from ..factory import target_factory
from .common import Driver
from .consoleexpectmixin import ConsoleExpectMixin
from ..step import step
from ..util.proxy import proxymanager
from ..resource import CANPort

@target_factory.reg_driver
@attr.s(eq=False)
class J1939Driver(ConsoleExpectMixin, Driver):
    """
    Driver implementing the interface over a CANPort connection
    """
    bindings = {"port": {"CANPort", "NetworkCANPort"}, }

    # TODO: add FD/SPEED support here
    # txdelay = attr.ib(default=0.0, validator=attr.validators.instance_of(float))
    # timeout = attr.ib(default=3.0, validator=attr.validators.instance_of(float))

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.ecu = None

    def on_activate(self):
        self.open()

    def on_deactivate(self):
        self.close()

    @Driver.check_bound
    def get_export_vars(self):
        export_vars = {
            "speed": str(self.port.speed)
        }
        if isinstance(self.port, CANPort):
            export_vars["port"] = self.port.port
        else:
            host, port = proxymanager.get_host_and_port(self.port)
            export_vars["host"] = host
            export_vars["port"] = str(port)
        return export_vars

    @Driver.check_active
    @step()
    def get_ecu(self):
        """Access underlying ECU."""
        return self.ecu

    @Driver.check_active
    @step()
    def stop(self):
        """Stop the ECU."""
        return self.ecu.stop()

    @Driver.check_active
    @step()
    def add_timer(self, delta_time, callback, cookie=None):
        """Add Timer."""
        return self.ecu.add_timer(delta_time, callback, cookie)

    @Driver.check_active
    @step()
    def remove_timer(self, callback):
        """Remove Timer."""
        return self.ecu.remove_timer(callback)

    @Driver.check_active
    @step()
    def connect(self, *args, **kwargs):
        """Connect to the ECU."""
        return self.ecu.connect(*args, **kwargs)

    @Driver.check_active
    @step()
    def disconnect(self):
        """Disconnect ECU."""
        return self.ecu.disconnect()

    @Driver.check_active
    @step()
    def unsubscribe(self, callback):
        """Unsubscribe callback."""
        return self.ecu.unsubscribe(callback)

    @Driver.check_active
    @step()
    def add_ca(self, **kwargs):
        """Add CA."""
        return self.ecu.add_ca(**kwargs)

    @Driver.check_active
    @step()
    def remove_ca(self, device_address):
        """Remove CA."""
        return self.ecu.remove_ca(device_address)

    @Driver.check_active
    @step()
    def add_bus(self, bus):
        """Add bus."""
        return self.ecu.add_bus(bus)

    @Driver.check_active
    @step()
    def add_notifier(self, notifier):
        """Add Notifier."""
        return self.ecu.add_notifier(notifier)

    @Driver.check_active
    @step()
    def remove_bus(self):
        """Remove bus."""
        return self.ecu.remove_bus()

    @Driver.check_active
    @step()
    def remove_notifier(self):
        """Remove Notifier."""
        return self.ecu.remove_notifier()

    @Driver.check_active
    @step()
    def send_pgn(self, data_page, pdu_format, pdu_specific, priority, src_address, data, time_limit=0, frame_format=j1939.message_id.FrameFormat.FEFF):
        """Send PGN."""
        return self.ecu.send_pgn(data_page, pdu_format, pdu_specific, priority, src_address, data, time_limit, frame_format)

    @Driver.check_active
    @step()
    def send_message(self, can_id, extended_id, data, fd_format=False):
        """Send Message."""
        return self.ecu.send_message(can_id, extended_id, data, fd_format)

    @Driver.check_active
    @step()
    def notify(self, can_id, data, timestamp):
        """Notify."""
        return self.ecu.notify(can_id, data, timestamp)

    def open(self):
        """Opens the can port, does nothing if it is already open"""
        if not self.ecu:
            self.ecu = j1939.ElectronicControlUnit()
            if isinstance(self.port, CANPort):
                self.ecu.connect(bustype="socketcan", channel=self.port.bus)
            else:
                host, port = proxymanager.get_host_and_port(self.port)
                self.ecu.connect(bustype="socketcand", channel=self.port.bus, host=host, port=port)

    def close(self):
        """Closes the can port, does nothing if it is already closed"""
        if self.ecu :
            self.ecu.disconnect()
            self.ecu = None

    def __str__(self):
        return f"J1939Driver({self.target.name})"
