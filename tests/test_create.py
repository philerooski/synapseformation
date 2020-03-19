"""
Tests creation module
Functions are named with the function name in create module along
with what is tested
"""
import json
import uuid

from challengeutils import utils
import mock
from mock import patch
import pytest
import synapseclient
from synapseclient.exceptions import SynapseHTTPError

from synapseformation.create import SynapseCreation

SYN = mock.create_autospec(synapseclient.Synapse)
CREATE_CLS = SynapseCreation(SYN)
GET_CLS = SynapseCreation(SYN, only_create=False)
# remove this later
UPDATE_CLS = SynapseCreation(SYN, only_create=False)


def test__find_by_name_or_create__create():
    """Tests creation"""
    entity = synapseclient.Entity(name=str(uuid.uuid1()))
    returned = synapseclient.Entity(name=str(uuid.uuid1()))
    with patch.object(SYN, "store", return_value=returned) as patch_syn_store:
        created_ent = CREATE_CLS._find_by_name_or_create(entity)
        patch_syn_store.assert_called_once_with(entity,
                                                createOrUpdate=False)
        assert created_ent == returned


def test__find_by_name_or_create__onlycreate_raise():
    """Tests only create flag raises error when entity exists"""
    entity = synapseclient.Entity(name=str(uuid.uuid1()))
    returned = synapseclient.Entity(name=str(uuid.uuid1()))
    with patch.object(SYN, "store", side_effect=SynapseHTTPError),\
         pytest.raises(ValueError, match="only_create is set to True."):
        CREATE_CLS._find_by_name_or_create(entity)


def test__find_by_name_or_create__get():
    """Tests only create flag raises error when entity exists"""
    concretetype = str(uuid.uuid1())
    entity = synapseclient.Entity(name=str(uuid.uuid1()),
                                  parentId=str(uuid.uuid1()),
                                  concreteType=concretetype)
    restpost = synapseclient.Entity(name=str(uuid.uuid1()),
                                    id=str(uuid.uuid1()),
                                    parentId=str(uuid.uuid1()))
    returned = synapseclient.Entity(name=str(uuid.uuid1()),
                                    id=str(uuid.uuid1()),
                                    parentId=str(uuid.uuid1()),
                                    concreteType=concretetype)
    body = json.dumps({"parentId": entity.properties.get("parentId", None),
                       "entityName": entity.name})
    with patch.object(SYN, "store", side_effect=SynapseHTTPError),\
         patch.object(SYN, "restPOST",
                      return_value=restpost) as patch_rest_post,\
         patch.object(SYN, "get", return_value=returned) as patch_rest_get:
        get_ent = GET_CLS._find_by_name_or_create(entity)
        assert get_ent == returned
        patch_rest_post.assert_called_once_with("/entity/child", body=body)
        patch_rest_get.assert_called_once_with(restpost.id, downloadFile=False)


def test_get_or_create_project__call():
    """Tests the correct parameters are passed in"""
    project_name = str(uuid.uuid1())
    project = synapseclient.Project(name=project_name)
    returned = synapseclient.Project(name=project_name,
                                     id=str(uuid.uuid1()))
    with patch.object(CREATE_CLS,
                      "_find_by_name_or_create",
                      return_value=returned) as patch_find_or_create:
        new_project = CREATE_CLS.get_or_create_project(name=project_name)
        assert new_project == returned
        patch_find_or_create.assert_called_once_with(project)


@pytest.mark.parametrize("invoke_cls,create",
                         [(CREATE_CLS, False), (UPDATE_CLS, True)])
def test_create_folder__call(invoke_cls, create):
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
                                                createOrUpdate=create)


@pytest.mark.parametrize("invoke_cls,create",
                         [(CREATE_CLS, False), (UPDATE_CLS, True)])
def test_create_file__call(invoke_cls, create):
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
                                                createOrUpdate=create)


def test_create_team__call():
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
        patch_syn_store.assert_called_once_with(team_ent,
                                                createOrUpdate=False)


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


def test_create_evaluation_queue__call():
    """Tests the correct parameters are passed in"""
    queue_name = str(uuid.uuid1())
    parentid = "syn" + str(uuid.uuid1())
    description = str(uuid.uuid1())
    queue = synapseclient.Evaluation(name=queue_name,
                                     contentSource=parentid,
                                     description=description,
                                     quota={})
    returned = synapseclient.Evaluation(name=queue_name,
                                        contentSource=parentid,
                                        id=str(uuid.uuid1()),
                                        description=description,
                                        quota={})
    with patch.object(SYN, "store", return_value=returned) as patch_syn_store:
        new_queue = CREATE_CLS.create_evaluation_queue(queue_name,
                                                       parentid=parentid,
                                                       description=description,
                                                       quota={})
        assert new_queue == returned
        patch_syn_store.assert_called_once_with(queue,
                                                createOrUpdate=False)


def test_create_evaluation_queue__fetch_call():
    """Tests the correct parameters are passed in for updating"""
    queue_name = str(uuid.uuid1())
    parentid = "syn" + str(uuid.uuid1())
    returned = synapseclient.Evaluation(name=queue_name,
                                        contentSource=parentid,
                                        id=str(uuid.uuid1()))
    with patch.object(SYN, "restGET",
                      return_value=returned) as patch_rest_get:
        new_team = UPDATE_CLS.create_evaluation_queue(queue_name,
                                                      parentid=parentid)
        patch_rest_get.assert_called_once_with(f"/evaluation/name/{queue_name}")
        assert new_team == returned


class Challenge:
    """mock challenge class"""
    id = str(uuid.uuid1())


def test_create_challenge_widget__call():
    """Tests the correct parameters are passed in for creation"""
    project_live = str(uuid.uuid1())
    team_part_id = str(uuid.uuid1())
    with patch.object(utils, "create_challenge",
                      return_value=Challenge) as patch_create_chal:
        chal = CREATE_CLS.create_challenge_widget(project_live, team_part_id)
        patch_create_chal.assert_called_once_with(SYN, project_live,
                                                  team_part_id)
        assert chal == Challenge


def test_create_challenge_widget__fetch_call():
    """Tests the correct parameters are passed in for fetching"""
    project_live = str(uuid.uuid1())
    team_part_id = str(uuid.uuid1())
    with patch.object(utils, "get_challenge",
                      return_value=Challenge) as patch_get_chal:
        chal = UPDATE_CLS.create_challenge_widget(project_live, team_part_id)
        patch_get_chal.assert_called_once_with(SYN, project_live)
        assert chal == Challenge


@pytest.mark.parametrize("invoke_cls,create",
                         [(CREATE_CLS, False), (UPDATE_CLS, True)])
def test_create_wiki__call(invoke_cls, create):
    """Tests the correct parameters are passed in"""
    title = str(uuid.uuid1())
    markdown = str(uuid.uuid1())
    projectid = str(uuid.uuid1())
    parent_wiki = str(uuid.uuid1())

    returned = synapseclient.Wiki(title=title,
                                  markdown=markdown,
                                  owner=projectid,
                                  parentWikiId=parent_wiki)
    with patch.object(SYN, "store", return_value=returned) as patch_syn_store:
        new_wiki = invoke_cls.create_wiki(title=title, projectid=projectid,
                                          markdown=markdown,
                                          parent_wiki=parent_wiki)
        assert new_wiki == returned
        patch_syn_store.assert_called_once_with(returned,
                                                createOrUpdate=create)
