import requests


class HTTPClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def _request(self, method, endpoint, params=None, data=None, json=None, headers=None):
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        response = requests.request(method, url, params=params, data=data, json=json, headers=headers)
        response.raise_for_status()  # Raise an exception for non-2xx responses
        return response

    def get(self, endpoint="", params=None, headers=None):
        return self._request('GET', endpoint, params=params, headers=headers)

    def post(self, endpoint="", data=None, json=None, headers=None):
        return self._request('POST', endpoint, data=data, json=json, headers=headers)

    def put(self, endpoint="", data=None, json=None, headers=None):
        return self._request('PUT', endpoint, data=data, json=json, headers=headers)

    def delete(self, endpoint="", headers=None):
        return self._request('DELETE', endpoint, headers=headers)
