import attr
from pexpect import TIMEOUT
import can
import subprocess
import logging

from ..factory import target_factory
from .common import Driver
from .consoleexpectmixin import ConsoleExpectMixin
from ..step import step
from ..util.proxy import proxymanager
from ..resource import CANPort
from ..labgridclientmanager import ClientManager

logger = logging.getLogger()

@target_factory.reg_driver
@attr.s(eq=False)
class CANDriver(ConsoleExpectMixin, Driver):
    """
    Driver implementing the interface over a CANPort connection
    """
    bindings = {"port": {"CANPort", "NetworkCANPort"}, }
    client = ClientManager()

    # TODO: add FD/SPEED support here
    # txdelay = attr.ib(default=0.0, validator=attr.validators.instance_of(float))
    # timeout = attr.ib(default=3.0, validator=attr.validators.instance_of(float))

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.bus = None

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
    def get_bus(self):
        """Access underlying bus."""
        return self.bus

    @Driver.check_active
    @step()
    def send(self, msg, timeout_sec=0):
        return self.bus.send(msg, timeout_sec)

    @Driver.check_active
    @step()
    def recv(self, timeout_sec=None):
        return self.bus.recv(timeout_sec)

    @Driver.check_active
    @step()
    def flush_rx_buffer(self):
        while self.bus.recv(0.001):
            pass
        return True

    @Driver.check_active
    @step()
    def flush_tx_buffer(self):
        return self.bus.flush_tx_buffer()

    @Driver.check_active
    @step()
    def set_filters(self, filters=None):
        return self.bus.set_filters(filters)

    @Driver.check_active
    @step()
    def send_periodic(self, msgs, period_sec, duration=None, store_task=True, autostart=True, modifier_callback=None):
        return self.bus.send_periodic(msgs, period_sec, duration, store_task, autostart, modifier_callback)

    @Driver.check_active
    @step()
    def stop_all_periodic_tasks(self, remove_tasks=True):
        return self.bus.stop_all_periodic_tasks(remove_tasks)

    def open(self):
        """Opens the can port, does nothing if it is already open"""
        if not self.bus:
            if isinstance(self.port, CANPort):
                self.bus = can.interface.Bus(bustype="socketcan", channel=self.port.bus)
            else:
                host, port = proxymanager.get_host_and_port(self.port)
                self.bus = can.interface.Bus(bustype="socketcand", channel=self.port.bus, host=host, port=port)

    def close(self):
        """Closes the can port, does nothing if it is already closed"""
        if self.bus :
            self.bus.shutdown()
            self.bus = None

    def create_interface(self, local_channel, local_channel_type):
        if not self.client.check_vcan(local_channel):
            logger.warning("Local can not present, setting up...")
            self.client.setup_vcan(local_channel, local_channel_type)
        else:
            logger.info("Local can present, skipping setup...")

        cmd = [
            "socketcandcl",
            "--verbose",
            "--server", str(self.port.host),
            "--port", str(self.port.port),
            "--interfaces", f"{self.port.bus},{local_channel}"
        ]

        self.socketcandcl = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        logger.info(f"socketcandcl started with PID {self.socketcandcl.pid}")

    def cleanup_interface(self):
        self.client.kill_process(self.socketcandcl)

    def __str__(self):
        return f"CANDriver({self.target.name})"
