"""
add directories to the incremental import "do not import" list
"""

import logging
import os.path

from beets import plugins, ui, importer
from beets.util import syspath, normpath, displayable_path

# Global logger.
log = logging.getLogger('beets')

class NoImportPlugin(plugins.BeetsPlugin):
    def __init__(self):
        super(NoImportPlugin, self).__init__()

        self._command = ui.Subcommand(
            'noimport',
            help='add directories to the incremental import "do not import" list')

    def commands(self):
        def func(lib, opts, args):
            # to match "beet import" function
            paths = args
            if not paths:
                raise ui.UserError('no path specified')

            self.noimport_files(lib, paths)

        self._command.func = func
        return [self._command]

    def noimport_files(self, lib, paths):
        # Check the user-specified directories.
        for path in paths:
            if not os.path.exists(syspath(normpath(path))):
                raise ui.UserError(u'no such file or directory: {0}'.format(
                    displayable_path(path)))

        # Open the state file
        state = importer._open_state()

        # Create the 'taghistory' set if it doesn't exist
        if 'taghistory' not in state:
            state['taghistory'] = set()

        # For every path...
        for path in paths:
            added = 0
            # ...get the list of albums in that path...
            for dirs, paths_in_dir in importer.albums_in_dir(path):
                # ...check if they're not already in the 'taghistory' set
                if tuple(dirs) not in state['taghistory']:
                    # ...and add them...
                    state['taghistory'].add(tuple(map(normpath, dirs)))
                    added += 1

        # Save the state file
        importer._save_state(state)

        log.info(u'Added {0} paths to the skip list', added)