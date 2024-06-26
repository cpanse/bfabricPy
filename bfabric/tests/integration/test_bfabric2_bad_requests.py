import json
import os
import unittest

from bfabric import Bfabric, BfabricAPIEngineType
from bfabric.errors import BfabricRequestError


class BfabricTestBadRequest(unittest.TestCase):
    def setUp(self):
        # Load ground truth
        path = os.path.join(os.path.dirname(__file__), "groundtruth.json")
        with open(path) as json_file:
            self.ground_truth = json.load(json_file)

        # Create clients
        self.clients = {
            "zeep": Bfabric.from_config("TEST", engine=BfabricAPIEngineType.ZEEP),
            "suds": Bfabric.from_config("TEST", engine=BfabricAPIEngineType.SUDS),
        }

    def _test_non_existing_read(self, engine_name: str):
        # NOTE: Currently a bad read request simply returns no matches, but does not throw errors
        res = self.clients[engine_name].read("user", {"id": "cat"}).to_list_dict()
        self.assertEqual([], res)

    def _test_forbidden_save(self, engine_name: str):
        # Test what happens if we save to an endpoint that does not accept saving
        self.assertRaises(BfabricRequestError, self.clients[engine_name].save, "project", {"name": "TheForbiddenPlan"})

    def _test_wrong_delete(self, engine_name: str):
        self.assertRaises(RuntimeError, self.clients[engine_name].delete, "workunit", 101010101010101)

    def test_non_existing_read_when_suds(self):
        self._test_non_existing_read("suds")

    def test_non_existing_read_when_zeep(self):
        self._test_non_existing_read("zeep")

    def test_forbidden_save_when_suds(self):
        self._test_forbidden_save("suds")

    def test_forbidden_save_when_zeep(self):
        self._test_forbidden_save("zeep")

    def test_wrong_delete_when_suds(self):
        self._test_wrong_delete("suds")

    def test_wrong_delete_when_zeep(self):
        self._test_wrong_delete("zeep")


if __name__ == "__main__":
    unittest.main(verbosity=2)
