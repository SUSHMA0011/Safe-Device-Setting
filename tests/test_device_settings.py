import unittest
from copy import deepcopy

from device_settings import apply_update


class TestDeviceSettings(unittest.TestCase):

    def setUp(self):
        self.current = {
            "deviceId": "D01",
            "siteId": "S01",
            "version": 3,
            "settings": {
                "language": "en",
                "volume": 2
            }
        }

        self.actor = {
            "role": "editor",
            "siteId": "S01"
        }

        self.request = {
            "deviceId": "D01",
            "expectedVersion": 3,
            "settings": {"volume": 4}
        }

    def test_successful_partial_update(self):
        status, result = apply_update(
            self.current, self.actor, self.request
        )

        self.assertEqual(status, 200)
        self.assertEqual(result["settings"]["volume"], 4)
        self.assertEqual(result["settings"]["language"], "en")
        self.assertEqual(result["version"], 4)

    def test_invalid_volume(self):
        self.request["settings"] = {"volume": 10}

        status, result = apply_update(
            self.current, self.actor, self.request
        )

        self.assertEqual(status, 422)
        self.assertEqual(self.current["version"], 3)

    def test_wrong_device(self):
        self.request["deviceId"] = "D99"

        status, result = apply_update(
            self.current, self.actor, self.request
        )

        self.assertEqual(status, 404)

    def test_stale_version(self):
        self.request["expectedVersion"] = 2

        status, result = apply_update(
            self.current, self.actor, self.request
        )

        self.assertEqual(status, 409)

    def test_unauthorized_actor(self):
        self.actor["role"] = "viewer"

        status, result = apply_update(
            self.current, self.actor, self.request
        )

        self.assertEqual(status, 403)


if __name__ == "__main__":
    unittest.main()