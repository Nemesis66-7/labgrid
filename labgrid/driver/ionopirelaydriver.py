import attr

from ..factory import target_factory
from ..resource.remote import RemoteIonopi
from ..step import step
from ..protocol import DigitalOutputProtocol
from ..util.agentwrapper import AgentWrapper
from .common import Driver


@target_factory.reg_driver
@attr.s(eq=False)
class IonopiRelayDriver(Driver, DigitalOutputProtocol):
    bindings = {
        "ionopi": {"Ionopi", RemoteIonopi},
    }

    index = attr.ib(validator=attr.validators.instance_of(int))

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.wrapper = None

        if self.index < 0 or self.index > 4:
            raise Exception(f"{self.index} index is invalid [1-4].")

    def on_activate(self):
        if isinstance(self.ionopi, RemoteIonopi):
            host = self.ionopi.host
        else:
            host = None
        self.wrapper = AgentWrapper(host)
        self.proxy = self.wrapper.load('ionopi')

    def on_deactivate(self):
        self.wrapper.close()
        self.wrapper = None
        self.proxy = None

    @Driver.check_active
    @step(args=['status'])
    def set(self, status):
        self.proxy.set_relay(self.index, status)

    @Driver.check_active
    @step(result=True)
    def get(self):
        return self.proxy.get_relay(self.index)

    def __str__(self):
        return f"IonopiRelayDriver({self.target.name})"