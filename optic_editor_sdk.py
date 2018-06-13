# import websocket
import json
import threading

try:
    import thread
except ImportError:
    import _thread as thread
import time


class EditorConnection(object):

    def context(self, filepath, start, end, content):
        if self.ws.sock.connected:
            self.ws.send(
                json.dumps({'event': 'context', 'file': filepath, 'start': start, 'end': end, 'content': content}))

    def search(self, filepath, start, end, content, query):
        if self.ws.sock.connected:
            self.ws.send(json.dumps(
                {'event': 'search', 'file': filepath, 'start': start, 'end': end, 'content': content, 'query': query}))

    def onFilesUpdated(self, callback):
        self.filesUpdatedCallbacks.append(callback)

    def _on_message(self, ws, message):
        payload = json.loads(message)
        if payload.event == 'files-updated':
            for c in self.filesUpdatedCallbacks:
                c(message)

        print(message)

    def _on_error(self, ws, error):
        print(error)

    def _on_close(self, ws):
        print(ws)
        print("### closed ###")

    def _on_open(self, ws):
        print(ws)
        print("### opened ###")

    def connect(self):
        print("TRYING TO CONNECT")
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("ws://localhost:30333/socket/editor/" + self.name, on_message=self._on_message,
                                         on_error=self._on_error, on_close=self._on_close)
        self.ws.on_open = self._on_open
        self.ws.run_forever()

    def _tryConnect(self):
        while True:
            if not hasattr(self, 'ws') or (hasattr(self, 'ws') and self.ws.sock is None):
                self.connect()
            if hasattr(self, 'ws') and self.ws.sock is not None and not self.ws.sock.connected:
                self.connect()
            time.sleep(10)

    def __init__(self, name):
        self.name = name
        self.filesUpdatedCallbacks = []
        self._tryConnect()

#
# def main():
#     connection = EditorConnection("pythonTest")
#
#
# main()
#
# if __name__ == '__main__':
#     while True:
#         try:
#             pass
#         except Exception as err:
#             # do any logging etc of err
#             pass
