import sublime, sublime_plugin
from . import optic_editor_sdk

class Optic(sublime_plugin.ViewEventListener):
  def on_load(view):
    editor_conn = optic_editor_sdk.EditorConnection("sublime_text")

    print(view.file_name(), "just got loaded")

  # Captures when a user is making edits to a file
  def on_modified(obj):
    view = obj.view
    file_content = view.substr(sublime.Region(0, view.size()))

    payload = {"event": "context", "file": view.file_name(), "start": view.sel()[0].begin(), "end": view.sel()[0].end(), "content": file_content}
    print(payload)

  # Captures when a user's cursor position changes or a selection is made
  def on_selection_modified(obj):
    view = obj.view
    file_content = view.substr(sublime.Region(0, view.size()))

    payload = {"event": "context", "file": view.file_name(), "start": view.sel()[0].begin(), "end": view.sel()[0].end(), "content": file_content}
    print(payload)

