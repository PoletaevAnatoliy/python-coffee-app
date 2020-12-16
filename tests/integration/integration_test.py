import unittest
from datetime import datetime
from multiprocessing import Process

from app import app
from server_connector import ServerConnector


class ClientServerConnectionTest(unittest.TestCase):

    @staticmethod
    def start_test_server():
        app.run(port=5050)

    def setUp(self):
        self.server = Process(target=ClientServerConnectionTest.start_test_server)
        self.server.start()

    def tearDown(self):
        self.server.terminate()

    @staticmethod
    def clear_breakages_from_id(breakages_list):
        return [{"place": breakage['place'], "time": breakage['time'], "description": breakage['description']}
                for breakage in breakages_list]

    def test_connection(self):
        place, time, description = "At station", int(datetime.now().timestamp()), "This is test breakage"
        client = ServerConnector("http://127.0.0.1", 5050, 1)
        self.assertTrue(client.add_breakage(place, int(time), description))
        self.assertIn({"place": place, "time": time, "description": description},
                      ClientServerConnectionTest.clear_breakages_from_id(client.get_free_breakages()))


if __name__ == '__main__':
    unittest.main()
