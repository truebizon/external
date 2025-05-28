import unittest
import os
import sys

TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
sys.path.insert(0, SRC_DIR)

from fc.telemetry.dji.cloud_api.telemetry_manager import TelemetryManagerImpl
from protocolbuffers.uas_common_pb2 import UasState

class ConvertModeToUasStateTest(unittest.TestCase):
    def setUp(self):
        self.manager = TelemetryManagerImpl()

    def test_landing_state(self):
        self.assertEqual(
            self.manager.convert_mode_to_uas_state(0, None),
            UasState.Value('LANDING')
        )

    def test_inflight(self):
        self.assertEqual(
            self.manager.convert_mode_to_uas_state(3, None),
            UasState.Value('INFLIGHT')
        )

    def test_inflight_mission_hover(self):
        self.assertEqual(
            self.manager.convert_mode_to_uas_state(3, 'mission'),
            UasState.Value('INFLIGHT_MISSION_HOVER')
        )

    def test_inflight_mission(self):
        self.assertEqual(
            self.manager.convert_mode_to_uas_state(4, 'mission'),
            UasState.Value('INFLIGHT_MISSION')
        )

    def test_inflight_mission_interrupt(self):
        self.assertEqual(
            self.manager.convert_mode_to_uas_state(99, 'mission'),
            UasState.Value('INFLIGHT_MISSION_INTERRUPT')
        )

if __name__ == '__main__':
    unittest.main()
