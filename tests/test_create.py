"""
Tests creation module
Functions are named with the function name in create module along
with what is tested
"""
import uuid

import mock
from mock import patch
import pytest
import synapseclient

from synapseformation.create import SynapseCreation

SYN = mock.create_autospec(synapseclient.Synapse)
CREATE_CLS = SynapseCreation(SYN)
UPDATE_CLS = SynapseCreation(SYN, create_or_update=True)


@pytest.mark.parametrize("invoke_cls", [CREATE_CLS, UPDATE_CLS])
def test_create_project__call(invoke_cls):
    """Tests the correct parameters are passed in"""
    project_name = str(uuid.uuid1())
    project = synapseclient.Project(name=project_name)
    returned = synapseclient.Project(name=project_name,
                                     id=str(uuid.uuid1()))
    with patch.object(SYN, "store", return_value=returned) as patch_syn_store:
        new_project = invoke_cls.create_project(project_name)
        assert new_project == returned
        patch_syn_store.assert_called_once_with(project,
                                                createOrUpdate=invoke_cls.create_or_update)

@pytest.mark.parametrize("invoke_cls", [CREATE_CLS, UPDATE_CLS])
def test_create_folder__call(invoke_cls):
    """Tests the correct parameters are passed in"""
    folder_name = str(uuid.uuid1())
    parentid = str(uuid.uuid1())
    folder = synapseclient.Folder(name=folder_name,
                                  parentId=parentid)
    returned = synapseclient.Folder(name=folder_name,
                                    id=str(uuid.uuid1()),
                                    parentId=parentid)
    with patch.object(SYN, "store", return_value=returned) as patch_syn_store:
        new_folder = invoke_cls.create_folder(folder_name, parentid)
        assert new_folder == returned
        patch_syn_store.assert_called_once_with(folder,
                                                createOrUpdate=invoke_cls.create_or_update)


@pytest.mark.parametrize("invoke_cls", [CREATE_CLS, UPDATE_CLS])
def test_create_file__call(invoke_cls):
    """Tests the correct parameters are passed in"""
    file_path = str(uuid.uuid1())
    parentid = str(uuid.uuid1())
    file_ent = synapseclient.File(path=file_path,
                                  parentId=parentid)
    returned = synapseclient.File(path=file_path,
                                  id=str(uuid.uuid1()),
                                  parentId=parentid)
    with patch.object(SYN, "store", return_value=returned) as patch_syn_store:
        new_file = invoke_cls.create_file(file_path, parentid)
        assert new_file == returned
        patch_syn_store.assert_called_once_with(file_ent,
                                                createOrUpdate=invoke_cls.create_or_update)


def test__create_team__call():
    """Tests the correct parameters are passed in"""
    team_name = str(uuid.uuid1())
    description = str(uuid.uuid1())
    can_public_join = True
    team_ent = synapseclient.Team(name=team_name,
                                  description=description,
                                  canPublicJoin=can_public_join)
    returned = synapseclient.Team(name=team_name,
                                  description=description,
                                  id=str(uuid.uuid1()),
                                  canPublicJoin=can_public_join)
    with patch.object(SYN, "store", return_value=returned) as patch_syn_store:
        new_team = CREATE_CLS.create_team(team_name, description=description,
                                          can_public_join=can_public_join)
        assert new_team == returned
        patch_syn_store.assert_called_once_with(team_ent)


def test__create_team__raise_error():
    """Error is raised when team name already exists"""
    team_name = str(uuid.uuid1())
    with patch.object(SYN, "store", side_effect=ValueError),\
         pytest.raises(ValueError, match=f"Team {team_name}*"):
        CREATE_CLS.create_team(team_name)


def test_create_team__call():
    """Tests the correct parameters are passed in"""
    team_name = str(uuid.uuid1())
    description = str(uuid.uuid1())
    can_public_join = True
    returned = synapseclient.Team(name=team_name,
                                  description=description,
                                  id=str(uuid.uuid1()),
                                  canPublicJoin=can_public_join)
    with patch.object(CREATE_CLS, "_create_team",
                      return_value=returned) as patch_create:
        new_team = CREATE_CLS.create_team(team_name, description=description,
                                          can_public_join=can_public_join)
        patch_create.assert_called_once_with(team_name,
                                             description=description,
                                             can_public_join=can_public_join)
        assert new_team == returned


def test_create_team__fetch_call():
    """Tests the correct parameters are passed in for updating"""
    team_name = str(uuid.uuid1())
    description = str(uuid.uuid1())
    can_public_join = True
    returned = synapseclient.Team(name=team_name,
                                  description=description,
                                  id=str(uuid.uuid1()),
                                  canPublicJoin=can_public_join)
    with patch.object(SYN, "getTeam",
                      return_value=returned) as patch_get_team:
        new_team = UPDATE_CLS.create_team(team_name, description=description,
                                          can_public_join=can_public_join)
        patch_get_team.assert_called_once_with(team_name)
        assert new_team == returned
