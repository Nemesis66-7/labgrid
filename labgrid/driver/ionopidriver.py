import attr

from ..factory import target_factory
from ..resource.remote import RemoteIonopi
from ..step import step
from ..util.agentwrapper import AgentWrapper
from .common import Driver


@target_factory.reg_driver
@attr.s(eq=False)
class IonopiDriver(Driver):
    bindings = {
        "ionopi": {"Ionopi", RemoteIonopi},
    }

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.wrapper = None

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
    @step(args=['index'])
    def get_relay(self, index):
        return self.proxy.get_relay(index)

    @Driver.check_active
    @step(args=['index', 'status'])
    def set_relay(self, index, status):
        return self.proxy.set_relay(index, status)

    @Driver.check_active
    @step(args=['index'])
    def get_adc_mv(self, index):
        return self.proxy.get_adc_mv(index)

    @Driver.check_active
    @step(args=['index', 'debounce_on_ms', 'debounce_off_ms'])
    def configure_digital_in(self, index, debounce_on_ms, debounce_off_ms):
        return self.proxy.configure_digital_in(index, debounce_on_ms, debounce_off_ms)

    @Driver.check_active
    @step(args=['index'])
    def get_digital_in(self, index):
        return self.proxy.get_digital_in(index)

    @Driver.check_active
    @step(args=['index'])
    def get_digital_in_on_count(self, index):
        return self.proxy.get_digital_in_on_count(index)

    @Driver.check_active
    @step(args=['index'])
    def get_digital_in_off_count(self, index):
        return self.proxy.get_digital_in_off_count(index)

    @Driver.check_active
    @step(args=['status'])
    def set_led(self, status):
        return self.proxy.set_led(status)

    @Driver.check_active
    @step(args=['on_ms', 'off_ms', 'rep'])
    def set_led_blink(self, on_ms, off_ms=0, rep=0):
        return self.proxy.set_led_blink(on_ms, off_ms, rep)

    @Driver.check_active
    @step(args=['index', 'status'])
    def set_oc(self, index, status):
        return self.proxy.set_oc(index, status)

    @Driver.check_active
    @step(args=['index'])
    def get_oc(self, index):
        return self.proxy.get_oc(index)
