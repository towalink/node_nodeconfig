# -*- coding: utf-8 -*-

"""Updates config files and starts, stops and restarts affected services"""

import logging
import os
import pprint

from . import exechelper
from . import fileupdater


logger = logging.getLogger(__name__);


class ServiceManager():
    """Updates config files and starts, stops and restarts affected services"""

    def __init__(self, confdir=None):
        """Constructor"""
        if confdir is None:
            self.confdir = '/etc/towalink/configs/v1'
        else:
            self.confdir = confdir
        self.exechelper = exechelper.ExecHelper()
        self.fileupdater = fileupdater.FileUpdater()

    def get_wginterface_by_filename(self, filename):
        """Returns the interface name for the given Wireguard config file name"""
        return filename.rpartition('.')[0] # strip file extension (".conf")

    def get_wgservice_by_filename(self, filename):
        """Returns the systemd service name for the given Wireguard config file name"""
        filename = self.get_wginterface_by_filename(filename)
        return f'wg-quick@{filename}'

    def update_startup(self):
        """Update the update_startup configuration scripts and activate changes"""

        def execute_file(item):
            """Prepares and executes the given file in the directory 'path_dst'"""
            filename = os.path.join(path_dst, item)
            os.chmod(filename, 0o744)
            out, err, returncode = self.exechelper.execute(filename, suppressoutput=True)
            if len(out) > 0:
                logger.debug(f'Output of [{item}]: ' + out)

        logger.debug('Updating startup scripts if needed')
        path_dst = '/opt/towalink/startup/scripts'
        files_new, files_changed, files_delete = self.fileupdater.update_files(self.confdir, path_dst, filter_prefix='startup_')
        assert len(files_delete) == 0, f'deletion of interface files is not supported [{files_delete}]'
        if len(files_new) + len(files_changed) + len(files_delete) > 0:
            logger.info(f'Executing interface scripts due to config file updates: {len(files_changed)} changed, {len(files_new)} new, {len(files_delete)} deleted')
            for item in files_new:
                execute_file(item)
            for item in files_changed:
                execute_file(item)
        return len(files_new) + len(files_changed) + len(files_delete)

    def update_wireguard(self):
        """Update Wireguard configuration files and activate changes"""
        logger.debug('Updating Wireguard if needed')
        # Stop and disable services if needed
        files_new, files_changed, files_delete = self.fileupdater.compare_files(self.confdir, '/etc/wireguard', filter_prefix='tlwg_', filter_suffix='.conf', filter_ignore=['tlwg_mgmt.conf'])
        if len(files_new) + len(files_changed) + len(files_delete) > 0:
            logger.info(f'Wireguard config file updates: {len(files_changed)} changed, {len(files_new)} new, {len(files_delete)} deleted')
        for item in files_delete:
            logger.info(f'Stopping and disabling service for Wireguard config [{item}]')
            #self.exechelper.disable_service(self.get_wgservice_by_filename(item))
            #self.exechelper.stop_service(self.get_wgservice_by_filename(item))
            self.exechelper.run_wgquick('down', self.get_wginterface_by_filename(item))
        for item in files_changed:
            logger.info(f'Stopping service for Wireguard config [{item}]')
            #self.exechelper.stop_service(self.get_wgservice_by_filename(item))
            self.exechelper.run_wgquick('down', self.get_wginterface_by_filename(item))
        # Update config files and start/enable services if needed
        files_new, files_changed, files_delete = self.fileupdater.update_files(self.confdir, '/etc/wireguard', filter_prefix='tlwg_', filter_suffix='.conf', filter_ignore=['tlwg_mgmt.conf'])
        for item in files_changed:
            logger.info(f'Starting service for Wireguard config [{item}]')
            #self.exechelper.start_service(self.get_wgservice_by_filename(item))
            self.exechelper.run_wgquick('up', self.get_wginterface_by_filename(item))
        for item in files_new:
            logger.info(f'Starting and enabling service for Wireguard config [{item}]')
            #self.exechelper.start_service(self.get_wgservice_by_filename(item))
            #self.exechelper.enable_service(self.get_wgservice_by_filename(item))
            self.exechelper.run_wgquick('up', self.get_wginterface_by_filename(item))

    def update_bird(self, force_reload=False):
        """Update Bird configuration files and activate changes"""
        logger.debug('Updating Bird if needed')
        files_new, files_changed, files_delete = self.fileupdater.update_files(self.confdir, '/etc', filter_prefix='bird', filter_suffix='.conf')        
        if force_reload or (len(files_new) + len(files_changed) + len(files_delete) > 0):
            logger.info(f'Reloading Bird configuration due to config file updates: {len(files_changed)} changed, {len(files_new)} new, {len(files_delete)} deleted')
            self.exechelper.reload_service('bird')

    def update_all(self):
        """Updates all configuration files and related services"""
        num_startup_updates = self.update_startup()
        self.update_wireguard()
        self.update_bird(force_reload=(num_startup_updates > 0))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s: %(message)s', level=logging.INFO)  # use %(name)s instead of %(module) to include hierarchy information, see 
    sm = ServiceManager()
    sm.update_all()
