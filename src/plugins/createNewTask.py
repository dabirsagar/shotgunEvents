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
        createTask,
        {"Shotgun_Task_Change": "sg_pipeline_ready"},
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


def createTask(sg, logger, event, args):
    """
    Assigns a HumanUser to a Project if that HumanUser is assigned to a Task
    which belongs to a Project s/he isn't already assigned to.

    :param sg: Shotgun API handle.
    :param logger: Logger instance.
    :param event: A Shotgun EventLogEntry entity dictionary.
    :param args: Any additional misc arguments passed through this plugin.

    {'type': 'Task', 'id': 6225, 'content': 'FX', 
    'step': {'id': 6, 'name': 'FX', 'type': 'Step'}, 'task_assignees': [], 
    'entity': {'id': 1339, 'name': '0010', 'type': 'Shot'}, 'project': {'id': 288, 'name': 'DummyTV', 'type': 'Project'}}

    """
    server = 'https://sagar.shotgrid.autodesk.com'
    script_name = 'readAccess'
    script_key = 'osayi0frbwuqiSizj#tiatdyz'

    # Make some vars for convenience.
    event_project = event.get("project")
    checkVal = event.get("meta", {}).get("new_value")

    #logger.info("Completed batch update at {0}".format(event))

    task_id = event.get("meta", {}).get('entity_id')
    taskFields = ['content', 'sg_status', 'step', 
                  'task_assignees', 'entity', 'project.Project.code', 'entity.Shot.sg_sequence',
                  'entity.Shot.sg_sequence.Sequence.episode', 'entity.Shot.code', 'entity.Asset.sg_asset_type']
    
    taskDict = sg.find("Task", [['id','is', task_id]], taskFields)[0]
    print(taskDict)

    if checkVal is True:
        sg = shotgun_api3.Shotgun(server, script_name=script_name, api_key=script_key)
        rootPath = '/home/admin/DirStructure_root/prod/projects'
        templatePath = '/home/admin/pipeline/Templates'

        if taskDict['entity']['type'] == 'Shot':
            # check if a project is episodic
            if taskDict['entity.Shot.sg_sequence.Sequence.episode'] is not None:
                taskPath = os.path.join(rootPath,taskDict['project.Project.code'], 'work', 
                                        'sequences',taskDict['entity.Shot.sg_sequence.Sequence.episode']['name'],
                                        taskDict['entity.Shot.sg_sequence']['name'], taskDict['entity.Shot.code'], 
                                        taskDict['step']['name'], taskDict['content']
                                        )
            else:
                taskPath = os.path.join(rootPath,taskDict['project.Project.code'], 'work', taskDict['entity.Shot.sg_sequence']['name'],
                                        'sequences', taskDict['entity.Shot.code'], taskDict['step']['name'], 
                                        taskDict['content']
                                        )
                
        elif taskDict['entity']['type'] == 'Asset':

                taskPath = os.path.join(rootPath,taskDict['project.Project.code'], 'work', 
                                        'assets', taskDict['entity.Asset.sg_asset_type'],
                                        taskDict['entity']['name'], taskDict['step']['name'],
                                        taskDict['content']
                                        )
        else:
            print('no entity found')
        print(taskPath)
        if not os.path.exists(taskPath):
            shutil.copytree((os.path.join(templatePath, 'taskTemplates', taskDict['step']['name'])), taskPath)
            logger.info("Task folder created at: \n {0}".format(taskPath))
        else:
            logger.error('{0} path already exists. Skipping folder creation.'.format(taskPath))

    else:
        logger.info("check val is false")

