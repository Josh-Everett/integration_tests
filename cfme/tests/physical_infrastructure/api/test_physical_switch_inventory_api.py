# -*- coding: utf-8 -*-
import pytest

from cfme.physical.provider.lenovo import LenovoProvider
from cfme.utils.rest import assert_response

pytestmark = [
    pytest.mark.tier(3),
    pytest.mark.provider([LenovoProvider])
]


def test_get_hardware(appliance, physical_switch):
    physical_switch.reload(attributes=['hardware'])
    assert_response(appliance)
    assert physical_switch.hardware is not None


@pytest.mark.parametrize('attribute', ['firmwares', 'nics', 'ports'])
def test_get_hardware_attributes(appliance, physical_switch, attribute):
    expanded_attribute = 'hardware.{}'.format(attribute)
    physical_switch.reload(attributes=[expanded_attribute])
    assert_response(appliance)
    assert physical_switch.hardware[attribute] is not None


def test_get_asset_detail(appliance, physical_switch):
    physical_switch.reload(attributes=['asset_detail'])
    assert_response(appliance)
    assert physical_switch.asset_detail is not None
