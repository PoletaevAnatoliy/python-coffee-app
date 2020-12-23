import requests


class SecurityError(Exception):
    pass


class ServerConnector:

    def __init__(self, address, port):
        self.url = f"{address}:{port}"
        self.user_id = None
        self._password = None
        self.user_role = None
        self.views = set()

        self._cached_free_breakages = []
        self._cached_engineers_breakages = []

    def set_user(self, user_id, user_password):
        result = requests.get(f"{self.url}/users/{user_id}",
                              json={'user_id': user_id,
                                    'password': user_password}).json()
        if result['status'] == 'error':
            if result['message'] == 'wrong user or password':
                raise SecurityError
            raise Exception
        self.user_id = user_id
        self._password = user_password
        self.user_role = result['role']

    def add_view(self, view):
        self.views.add(view)

    def update_data(self):
        if self.user_id is None:
            return
        self._cached_free_breakages = requests.get(f"{self.url}/breakages").json()
        self._cached_engineers_breakages = requests.get(f"{self.url}/user/{self.user_id}/breakages").json()
        for view in self.views:
            view.update_data()

    def get_free_breakages(self):
        return self._cached_free_breakages

    def get_taken_breakages(self):
        return self._cached_engineers_breakages

    def add_breakage(self, place, time: int, description):
        result = requests.post(f"{self.url}/breakages",
                               json={
                                   'place': place,
                                   'time': time,
                                   'description': description
                               }).json()
        self.update_data()
        return result['status'] == 'ok'

    def take_breakage(self, breakage_id):
        result = requests.post(f"{self.url}/breakages/{breakage_id}/take",
                               json={
                                   'user_id': self.user_id
                               }).json()

        self.update_data()
        return result['status'] == 'ok'

    def fix_breakage(self, breakage_id):
        requests.post(f"{self.url}/breakages/{breakage_id}/fix")
        self.update_data()
        return True

    def get_breakages_in_work(self):
        return []
