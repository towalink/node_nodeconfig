# -*- coding: utf-8 -*-

"""Class for comparing and mirroring files"""

import filecmp
import logging
import os
import pprint
import shutil


logger = logging.getLogger(__name__);


class FileUpdater():
    """Class for comparing and mirroring files"""

    def compare_files(self, path_src, path_dst, filter_prefix='', filter_suffix='', filter_ignore=None, no_jinja=True):
        """Compare files in the given directories and return the result"""
        # Get lists of files in the two directories
        files_src = os.listdir(path_src)
        files_dst = os.listdir(path_dst)
        # Filter for files we're looking for and return as a set
        if filter_ignore is None:
            filter_ignore = []
        files_src = { item for item in files_src if item.startswith(filter_prefix) and item.endswith(filter_suffix) and not (item in filter_ignore) and (not no_jinja or not item.endswith('.jinja'))}
        files_dst = { item for item in files_dst if item.startswith(filter_prefix) and item.endswith(filter_suffix) and not (item in filter_ignore) and (not no_jinja or not item.endswith('.jinja'))}
        # Find new and deleted files
        files_new = files_src - files_dst
        files_delete = files_dst - files_src
        # Compare files that are present in both directories
        files_changed = files_src.intersection(files_dst)
        files_changed = { item for item in files_changed if not filecmp.cmp(os.path.join(path_src, item), os.path.join(path_dst, item)) }
        # Return result
        return files_new, files_changed, files_delete

    def delete_files(self, files_delete, path):
        """Delete the given files (list) in the given directory"""
        for item in files_delete:
            os.remove(os.path.join(path, item))

    def update_files(self, path_src, path_dst, filter_prefix='', filter_suffix='', filter_ignore=None, do_delete=True, no_jinja=True):
        """Update files in the destination directory based on the files in the source directory and return the number of updates"""
        files_new, files_changed, files_delete = self.compare_files(path_src, path_dst, filter_prefix, filter_suffix, filter_ignore, no_jinja=no_jinja)
        # Copy new files from source to destination
        for item in files_new:
            shutil.copy2(os.path.join(path_src, item), os.path.join(path_dst, item))
        # Copy changed files from source to destination
        for item in files_changed:
            shutil.copy2(os.path.join(path_src, item), os.path.join(path_dst, item))       
        # Delete files in destination that no longer exist in source
        if do_delete:
            self.delete_files(files_delete, path_dst)
        # Return result
        return files_new, files_changed, files_delete


if __name__ == '__main__':
    fu = FileUpdater()
    print(fu.compare_files('/storage2/maindata/dirk/AnnikaDirk/Versionsverwaltung/towalink/nodecfg/src/nodecfg/test1', '/storage2/maindata/dirk/AnnikaDirk/Versionsverwaltung/towalink/nodecfg/src/nodecfg/test2', 'tlwg_', '.txt'))
    print(fu.update_files('/storage2/maindata/dirk/AnnikaDirk/Versionsverwaltung/towalink/nodecfg/src/nodecfg/test1', '/storage2/maindata/dirk/AnnikaDirk/Versionsverwaltung/towalink/nodecfg/src/nodecfg/test2', 'tlwg_', '.txt'))
