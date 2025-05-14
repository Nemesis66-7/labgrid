import attr

from ..factory import target_factory
from .common import Resource
from ..util.agents.ionopi import Ionopi

import logging
logger = logging.getLogger()

@target_factory.reg_resource
@attr.s(eq=False)
class Ionopi(Resource):
    """Resource for Ionopi drivers

    Args:
        None
    """
    pass