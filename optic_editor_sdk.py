import sublime
import sublime_plugin


import websocket
import json
import threading
import re

import time


class EditorConnection(object):

    def check_for_search(self, line, start, end):
        search_re = re.compile("^[\s]*\/\/\/[\s]*(.+)")
        match = search_re.match(line)
        is_search = (start == end) and match is not None
        return {
            'is_search': is_search,
            'query': match.groups()[0].strip() if (match is not None) else None,
        }

    def context(self, file, start, end, contents):
        if self.ws.sock and self.ws.sock.connected:
            self.ws.send(
                json.dumps({'event': 'context', 'file': file, 'start': start, 'end': end, 'contents': contents}))

    def search(self, file, start, end, contents, query):
        if self.ws.sock and self.ws.sock.connected:
            self.ws.send(json.dumps(
                {'event': 'search', 'file': file, 'start': start, 'end': end, 'contents': contents, 'query': query}))

    def on_files_updated(self, callback):
        self.files_updated_callbacks.append(callback)

    def _on_message(self, ws, message):
        # print(message)
        payload = json.loads(message)
        if payload['event'] == 'files-updated':
            for c in self.files_updated_callbacks:
                c(payload)

    def _on_error(self, ws, error):
        # print("### error ###")
        # print(error)

    def _on_close(self, ws):
        # print(ws)
        print("### closed optic connection ###")

    def _on_open(self, ws):
        print(ws)
        print("### opened optic connection ###")

    def connect(self):
        self.ws = websocket.WebSocketApp("ws://localhost:30333/socket/editor/" + self.name, on_message=self._on_message,
                                         on_error=self._on_error, on_close=self._on_close)
        self.ws.on_open = self._on_open
        self.ws.run_forever()

    def _try_connect(self):
        while True:
            if not hasattr(self, 'ws') or (hasattr(self, 'ws') and self.ws.sock is None):
                self.connect()
            if hasattr(self, 'ws') and self.ws.sock is not None and not self.ws.sock.connected:
                self.connect()
            time.sleep(10)

    def __init__(self, name):
        self.name = name
        self.files_updated_callbacks = []
        threading.Thread(target=self._try_connect).start()