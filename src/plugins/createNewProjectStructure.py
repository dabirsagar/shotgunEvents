# Copyright 2018 Autodesk, Inc.  All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license agreement
# provided at the time of installation or download, or which otherwise accompanies
# this software in either electronic or hard copy form.
#

# See docs folder for detailed usage info.

import os
import shotgun_api3
import shutil
# server = 'https://sagar.shotgrid.autodesk.com'
# script_name = 'readAccess'
# script_key = 'osayi0frbwuqiSizj#tiatdyz'

def registerCallbacks(reg):
    
    """
    Register our callbacks.

    :param reg: A Registrar instance provided by the event loop handler.
    """

    # Grab authentication env vars for this plugin. Install these into the env
    # if they don't already exist.
    # server = os.environ["SG_SERVER"]
    # script_name = os.environ["SGDAEMON_ASSIGNTOPROJECT_NAME"]
    # script_key = os.environ["SGDAEMON_ASSIGNTOPROJECT_KEY"]

    server = 'https://sagar.shotgrid.autodesk.com'
    script_name = 'readAccess'
    script_key = 'osayi0frbwuqiSizj#tiatdyz'

    # Grab an sg connection for the validator.
    sg = shotgun_api3.Shotgun(server, script_name=script_name, api_key=script_key)

    # Bail if our validator fails.
    if not is_valid(sg, reg.logger):
        reg.logger.warning("Plugin is not valid, will not register callback.")
        return

    # Register our callback with the Shotgun_%s_Change event and tell the logger
    # about it.
    reg.registerCallback(
        script_name,
        script_key,
        createProject,
        {"Shotgun_Project_Change": "sg_pipeline_ready"},
        None,
    )
    reg.logger.debug("Registered callback.")


def is_valid(sg, logger):
    """
    Validate our args.

    :param sg: Shotgun API handle.
    :param logger: Logger instance.
    :returns: True if plugin is valid, None if not.
    """

    # Make sure we have a valid sg connection.
    try:
        sg.find_one("Project", [])
    except Exception as e:
        logger.warning(e)
        return

    return True


def createProject(sg, logger, event, args):
    """
    Assigns a HumanUser to a Project if that HumanUser is assigned to a Task
    which belongs to a Project s/he isn't already assigned to.

    :param sg: Shotgun API handle.
    :param logger: Logger instance.
    :param event: A Shotgun EventLogEntry entity dictionary.
    :param args: Any additional misc arguments passed through this plugin.
    """
    server = 'https://sagar.shotgrid.autodesk.com'
    script_name = 'readAccess'
    script_key = 'osayi0frbwuqiSizj#tiatdyz'

    # Make some vars for convenience.
    event_project = event.get("project")
    checkVal = event.get("meta", {}).get("new_value")

    #logger.info("Completed batch update at {0}".format(event))

    # Bail if we don't have the info we need.
    # if not event_project or not checkVal:
    #     return
    project_id = event.get("meta", {}).get('entity_id')
    projDict = sg.find("Project", [['id','is', project_id]], ['code', 'sg_status', 'name'])[0]

    if projDict['code'] == None:
        logger.info("Project code is not set. Skipping folder creation for  \n {0}".format(projDict['name']))
        return

    if checkVal is True:
        sg = shotgun_api3.Shotgun(server, script_name=script_name, api_key=script_key)
        rootPath = '/home/admin/DirStructure_root/prod/projects'
        
        templatePath = '/home/admin/pipeline/Templates'
        
        code = projDict['code']
        if str(projDict['sg_status']) == 'Active':
            projPath = os.path.join(rootPath, code)
            if not os.path.exists(projPath):
                shutil.copytree((os.path.join(templatePath, 'template01')), os.path.join(rootPath,code))
                logger.info("Project folder created at: \n {0}".format(projPath))
            else:
                logger.info('{0} path already exists. Skipping folder creation.'.format(projPath))
        else:
            logger.warning('project {0} not active...Skipping folder creation.'.format(code))
            return

    else:
        logger.info("check val is false")

