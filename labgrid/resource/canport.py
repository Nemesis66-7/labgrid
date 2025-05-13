import attr

from ..factory import target_factory
from .common import Resource, NetworkResource
from .base import CANPort


@target_factory.reg_resource
@attr.s(eq=False)
class RawCANPort(CANPort, Resource):
    """RawCANPort describes a can port which is available on the local computer."""
    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        if self.bus is None:
            raise ValueError("RawCANPort must be configured with a bus")

# This does not derive from CANPort because it is not directly accessible
@target_factory.reg_resource
@attr.s(eq=False)
class NetworkCANPort(NetworkResource):
    """A NetworkCANPort is a remotely accessible canport via socketcand

    Args:
        port (int): socketcand port to connect to
        bus (str): can bus to connect to
        speed (int): speed of the bus e.g. 500000
    """
    port = attr.ib(validator=attr.validators.optional(attr.validators.instance_of(int)))
    bus = attr.ib(validator=attr.validators.optional(attr.validators.instance_of(str)))
    speed = attr.ib(default=500000, validator=attr.validators.instance_of(int))
