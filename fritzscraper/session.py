import binascii
import hashlib
import logging
import xml.etree.ElementTree as ET

import pandas as pd
import requests

from typing import Tuple

logger = logging.getLogger(__name__)


class AuthenticationError(RuntimeError):
    pass


def _columns_from_first_row(df: pd.DataFrame) -> pd.DataFrame:
    df_header = df.iloc[0]
    df = df[1:]
    df.columns = df_header
    return df


class FritzSession:
    def __init__(self, host: str, user: str, password: str):
        self._host = host
        self._user = user
        self._password = password

        self._sid = None

        self._session = requests.Session()
        self._login()

    def _try_get(self, url, **kwargs):
        response = self._session.get(url, **kwargs)

        # Reauthenticate when session expires
        if response.status_code == 403:
            logging.warning('Authentication error, trying to reauthenticate')
            self._login()
            response = self._session.get(url, **kwargs)

        return response

    def _try_post(self, url, **kwargs):
        response = self._session.post(url, **kwargs)

        # Reauthenticate when session expires
        if response.status_code == 403:
            logging.warning('Authentication error, trying to reauthenticate')
            self._login()
            response = self._session.post(url, **kwargs)

        return response

    def _login(self):
        logger.info(f'Logging in to host {self._host} with user {self._user}')

        challenge_response = self._session.get(f'http://{self._host}/login_sid.lua')
        challenge_response.raise_for_status()

        challenge_xml = ET.fromstring(challenge_response.text)
        challenge = challenge_xml.find('Challenge').text

        response_input = f"{challenge}-{self._password}"
        response_digest = hashlib.md5(response_input.encode('utf-16le')).digest()
        response = binascii.hexlify(response_digest).decode('ascii')

        session_response = self._session.post(f'http://{self._host}/login_sid.lua', data={
            'response': f'{challenge}-{response}',
            'username': self._user
        })
        session_response.raise_for_status()

        session_xml = ET.fromstring(session_response.text)
        sid = session_xml.find('SID').text

        if sid == 16 * '0':
            raise AuthenticationError()

        logger.info(f'Logged in successfully with SID {sid}')

        self._sid = sid

    def docsis_info(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        logger.info(f'Retrieving DOCSIS info')

        resp = self._try_get(f'http://{self._host}/internet/docsis_info.lua',
                             params={'sid': self._sid, 'xhr': 1, 'update': 'uiInfo'})
        resp.raise_for_status()

        rx_names, rx_data, tx_names, tx_data = pd.read_html(resp.text)

        rx = _columns_from_first_row(pd.concat([rx_names, rx_data], axis=1).T.dropna())
        tx = _columns_from_first_row(pd.concat([tx_names, tx_data], axis=1).T.dropna())

        return rx, tx
