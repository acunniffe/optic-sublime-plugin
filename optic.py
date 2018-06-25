import sys
import os
sys.path.append(os.path.dirname(__file__))

import itertools
from time import sleep
from subprocess import Popen

import sublime, sublime_plugin
from . import optic_editor_sdk


editor_conn = optic_editor_sdk.EditorConnection("sublime_text")

class Optic(sublime_plugin.ViewEventListener):
  def on_load(view):
    pass

  # Captures when a user is making edits to a file
  # def on_modified(obj):
  #   view = obj.view
  #   file_content = view.substr(sublime.Region(0, view.size()))
  #   line = view.substr(view.line(view.sel()[0]))

  #   payload = {"file": view.file_name(), "start": view.sel()[0].begin(), "end": view.sel()[0].end(), "content": file_content}
  #   search_result = editor_conn.check_for_search(line, payload['start'], payload['end'])
    
  #   if not(search_result['is_search']):
  #     print(payload)
  #     editor_conn.context(**payload)
  #   else:
  #     payload['query'] = search_result['query']
  #     print(payload)
  #     editor_conn.search(**payload)


  # Captures when a user's cursor position changes or a selection is made
  def on_selection_modified(obj):
    view = obj.view
    file_content = view.substr(sublime.Region(0, view.size()))

    payload = {"file": view.file_name(), "start": view.sel()[0].begin(), "end": view.sel()[0].end(), "contents": file_content}
    
    # print(payload)
    editor_conn.context(**payload)

def focus_view(v):
  if sublime.platform() == 'osx':
      name = 'Sublime Text'
      if int(sublime.version()) < 3000:
          name = 'Sublime Text 2'
      cmd = "/usr/bin/osascript -e 'tell application \"%s\" to activate'" % name
      # print(cmd)
      os.system(cmd)
  window = v.window()
  window.focus_view(v)
  window.focus_group(window.active_group()) 
  window.focus_view(v)

# Handle files updated event
def files_were_updated(payload):
  windows = sublime.windows()
  views = list(itertools.chain.from_iterable([window.views() for window in windows]))
  views = [v for v in views if v and v.file_name()]
  for update_file in payload['updates']:
    update_content = payload['updates'][update_file]
    file_was_open = False
    for v in views:
      if v.file_name() == update_file:
        focus_view(v)
        if v.sel()[0].end() > v.sel()[0].begin():
          # print("Updating selection after updates...")
          new_context_payload = {"file": v.file_name(), "start": v.sel()[0].begin(), "end": v.sel()[0].end(), "contents": update_content} 
          # print(new_context_payload)
          editor_conn.context(**new_context_payload)
        file_was_open = True
    if not(file_was_open):
      v = sublime.active_window().open_file(update_file)
      while v.is_loading():
        sleep(.1)
      focus_view(v)


editor_conn.on_files_updated(files_were_updated)