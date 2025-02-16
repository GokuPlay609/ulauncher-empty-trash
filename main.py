import logging
import subprocess
import distutils.spawn
import os
import shutil
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

logger = logging.getLogger(__name__)

class SystemManagementDirect(Extension):
    def __init__(self):
        logger.info('Loading Gnome Settings Extension')
        super(SystemManagementDirect, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        keyword = event.get_keyword()

        for id, kw in extension.preferences.items():
            if kw == keyword:
                self.on_match(id)
                return HideWindowAction()

    def on_match(self, id):
        if id == 'empty-trash':
            # Show confirmation dialog using zenity
            confirm = subprocess.run(
                ['zenity', '--question',
                 '--title', 'Empty Trash',
                 '--text', 'Are you sure you want to empty the trash?\nThis action cannot be undone.',
                 '--width', '300'],
                capture_output=True
            )

            # Only proceed if user clicked Yes (return code 0)
            if confirm.returncode == 0:
                trash_path = os.path.expanduser('~/.local/share/Trash')
                for subdir in ['files', 'info']:
                    path = os.path.join(trash_path, subdir)
                    if os.path.exists(path):
                        for item in os.listdir(path):
                            item_path = os.path.join(path, item)
                            try:
                                if os.path.isfile(item_path) or os.path.islink(item_path):
                                    os.unlink(item_path)
                                elif os.path.isdir(item_path):
                                    shutil.rmtree(item_path)
                            except Exception as e:
                                logger.error(f"Error removing {item_path}: {e}")

SystemManagementDirect().run()
