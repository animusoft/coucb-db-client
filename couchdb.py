# Copyright (C) Animusoft Corporation - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited. Proprietary and confidential.
# http://www.animusoft.com

"""
Native Python 3.4 CouchDB 1.5.0 Client

 This client is designed to be used with Python 3.4. It uses the following modules to support this feature

 - requests.py (http://docs.python-requests.org/)
 - json (built in)
"""

import uuid
import string
import json
import requests
import datetime
from enum import Enum, unique


class CouchDBError(Exception):
    # TODO: add ability to serialize to json
    # TODO: add ability to serialize to xml
    # TODO: add ability to serialize to string

    __created = datetime
    __id = string
    __title = string
    __description = string
    __stackTrace = string

    def __get_created(self) -> datetime:
        return self.__created

    def __get_id(self) -> string:
        return self.__id

    def __get_title(self) -> string:
        return self.__title

    def __set_title(self, value: string=None):
        self.__title = value

    def __get_description(self) -> string:
        return self.__description

    def __set_description(self, value: string=None):
        self.__description = value

    def __get_stack_trace(self) -> string:
        return self.__stackTrace

    def __set_stack_trace(self, value: string=None):
        self.__stackTrace = value

    created = property(__get_created)
    id = property(__get_id)
    title = property(__get_title, __set_title)
    description = property(__get_description, __set_description)
    stack_trace = property(__get_stack_trace, __set_stack_trace)


class CouchDB(object):
    committed_update_seq = int
    compact_running = bool
    data_size = int
    db_name = string
    disk_format_version = int
    disk_size = float
    doc_count = int
    doc_del_count = int
    instance_start_time = float
    purge_seq = int
    update_seq = int


class CouchDBDocument(object):
    id = string
    rev = string
    json = None
    attachments = list
    deleted = bool
    revisions = dict
    revs_info = list
    conflicts = None
    deleted_conflicts = None
    local_seq = None

    def __get_json_text(self):
        return json.dumps(self.json, default=lambda o: o.__dict__, sort_keys=True, indent="\t")

    json_text = property(__get_json_text)


@unique
class RevisionInfoStatus(Enum):
    Available = "available"
    Missing = "missing"
    Deleted = "deleted"
    Unknown = "unknown"


class RevisionInfo(object):
    rev = string
    status = RevisionInfoStatus


class NativeCouchDBManager(object):
    # region Instance Fields
    __name = string
    __user = string
    __password = string
    __host = string
    __port = int
    __full_commit = bool
    __auth_method = string
    __verify = bool
    __generate_uuid_from_couch = bool
    __supported_version = "1.5.0"
    __throw_errors = bool
    # endregion

    def __init__(self,
                 db_name: string="db-test",
                 db_user: string=None,
                 db_password: string=None,
                 db_host_ip: string="127.0.0.1",
                 db_host_port: int=5984,
                 db_full_commit: bool=True,
                 db_auth_method: string="basic",
                 db_verify: bool=False,
                 db_generated_uuid_from_couch_db: bool=True,
                 db_throw_errors: bool=False):
        """
        Initializes the CouchDB manager

        :param db_name: the name of the database
        :param db_user: the user to use when accessing the database
        :param db_password: the password for the user
        :param db_host_ip: the ip address of the couch db server
        :param db_host_port: the port of the couch db server
        :param db_full_commit:
        :param db_auth_method: the authentication method to use
        :param db_verify:
        :param db_generated_uuid_from_couch_db: generate uuids internally or through couchdb
        :param db_throw_errors: throw errors or suppress them
        """
        self.__name = db_name
        self.__user = db_user
        self.__password = db_password
        self.__host = db_host_ip
        self.__port = db_host_port
        self.__full_commit = db_full_commit
        self.__auth_method = db_auth_method
        self.__verify = db_verify
        self.__generate_uuid_from_couch = db_generated_uuid_from_couch_db
        self.__throw_errors = db_throw_errors

    def __get_command_text(self, cmd: string=None) -> string:
        return "http://" + self.__host + ":" + self.__port.__str__() + cmd

    # region Not Implemented

    # def retrieve_current_document_revision(self, database_name, doc_id):
    #     # HEAD /somedatabase/some_doc_id HTTP/1.0
    #
    #     # HTTP/1.1 200 OK
    #     # Etag: "946B7D1C"
    #     # Date: Thu, 17 Aug 2006 05:39:28 +0000GMT
    #     # Content-Type: application/json
    #     # Content-Length: 256
    #     pass

    # GET /somedatabase/_changes HTTP/1.0

    # HTTP/1.1 200 OK
    # Date: Fri, 8 May 2009 11:07:02 +0000GMT
    # Content-Type: application/json
    # Connection: close
    #
    # {"results":[
    # {"seq":1,"id":"fresh","changes":[{"rev":"1-967a00dff5e02add41819138abb3284d"}]},
    # {"seq":3,"id":"updated","changes":[{"rev":"2-7051cbe5c8faecd085a3fa619e6e6337"}]},
    # {"seq":5,"id":"deleted","changes":[{"rev":"2-eec205a9d413992850a6e32678485900"}],"deleted":true}
    # ],
    # "last_seq":5}

    # def retrieve_document_revision(self, database_name: string=None, doc_id: string=None):
    #     pass

    #endregion

    def retrieve_uuid(self, count: int=None) -> string:
        """
        Retrieves / Generates a UUID from CouchDB. If one cannot be generating

        :param count: An integer representing the number of UUIDs to retrieve
        :return: A string of a UUID if count is None, A list of UUIDs if count is not None, None otherwise
        """

        #region Sample Req/Resp
        #curl -X GET http://127.0.0.1:5984/_uuids

        #{"uuids":["6e1295ed6c29495e54cc05947f18c8af"]}
        #endregion

        result = None

        if not self.__generate_uuid_from_couch:
            result = uuid.uuid1().__str__()
        else:
            command_text = self.__get_command_text("/_uuids")
            payload = {"count": count}
            req = requests.get(command_text, params=payload)
            status_code = req.status_code

            if status_code == 200:

                json_result = req.json()

                if count is None:
                    result = json_result["uuids"][0]
                else:
                    result = json_result["uuids"]

            else:
                if self.__throw_errors is True:
                    cdb_error = CouchDBError()
                    cdb_error.title = "Failed to retrieve a uuid from CouchDB"
                    raise cdb_error
                else:
                    result = uuid.uuid1().__str__()

        return result

    def retrieve_status(self) -> string:
        """
        Retrieves the current status of Couch DB.

        :return: None if not available otherwise the version of Couch DB as a string
        """

        #region Sample Req/Resp
        # http://127.0.0.1:5984/

        # {
        #   "couchdb": "Welcome",
        #   "uuid": "85fb71bf700c17267fef77535820e371",
        #   "vendor": {
        #       "name": "The Apache Software Foundation",
        #       "version": "1.5.0"
        #   },
        #   "version": "1.5.0"
        # }
        #endregion

        connect_string = self.__get_command_text("")
        req = requests.get(connect_string)
        status_code = req.status_code
        reason = req.reason

        if status_code == 200 and reason == "OK":
            json_result = req.json()
            version = json_result['version']
        else:
            if self.__throw_errors is True:
                cdb_error = CouchDBError()
                cdb_error.title = "Unable to get the CouchDB server status"
                raise cdb_error
            else:
                version = None

        return version

    def create_database(self, database_name: string=None) -> bool:
        """
        Creates a database in CoucbDB

        :param database_name: The name to give to the new CouchDB database
        :return: True if created, False if already exists, None if unknown
        """

        #region Sample Req/Resp
        #PUT http://127.0.0.1:5984/database_name

        #{"ok":true}
        #{"error":"file_exists","reason":"The database could not be created, the file already exists."}
        #endregion

        result = None
        command_text = self.__get_command_text("/" + database_name)
        req = requests.put(command_text)
        status_code = req.status_code

        if status_code == 201 or status_code == 200:
            #201 Created – Database created successfully
            result = True
        else:
            json_result = req.json()
            result = False
            error = json_result["error"]
            reason = json_result["reason"]

            if self.__throw_errors is True:

                cdb_error = CouchDBError()
                cdb_error.description = "[" + error + "] " + reason

                if status_code == 400:
                    cdb_error.title = "400 Bad Request – Invalid database name"
                elif status_code == 401:
                    cdb_error.title = "401 Unauthorized – CouchDB Server Administrator privileges required"
                elif status_code == 412:
                    cdb_error.title = "412 Precondition Failed – Database already exists"
                else:
                    cdb_error.title = "An unknown status code was encountered : " + status_code

                raise cdb_error

        return result

    def delete_database(self, database_name: string=None) -> bool:
        """
        Deletes a database in CouchDB

        :param database_name: A string representation of the database name to be deleted
        :return: True if deleted, False if not, otherwise None for unknown
        """

        #region Sample Req/Resp
        #DELETE http://127.0.0.1:5984/database_name

        #{"ok":true}
        #endregion

        result = None
        command_text = self.__get_command_text("/" + database_name)
        req = requests.delete(command_text)
        status_code = req.status_code

        if status_code == 200:
            #200 OK – Database removed successfully
            result = True
        else:
            json_result = req.json()
            result = False
            error = json_result["error"]
            reason = json_result["reason"]

            if self.__throw_errors is True:

                cdb_error = CouchDBError()
                cdb_error.description = "[" + error + "] " + reason

                if status_code == 400:
                    cdb_error.title = "400 Bad Request – Invalid database name"
                elif status_code == 401:
                    cdb_error.title = "401 Unauthorized – CouchDB Server Administrator privileges required"
                elif status_code == 404:
                    cdb_error.title = "404 Not Found – Database doesn’t exist"
                else:
                    cdb_error.title = "An unknown status code was encountered : " + status_code

                raise cdb_error

        return result

    def retrieve_all_databases(self) -> list:
        """
        Retrieve all databases found in CouchDB

        :return: A list of strings representing the name for each database, None otherwise
        """

        #region Sample Req/Resp
        #GET /_all_dbs

        # HTTP/1.1 200 OK
        # Cache-Control: must-revalidate
        # Content-Length: 52
        # Content-Type: application/json
        # Date: Sat, 10 Aug 2013 06:57:48 GMT
        # Server: CouchDB (Erlang/OTP)
        #
        # [
        #    "_users",
        #    "contacts",
        #    "docs",
        #    "invoices",
        #    "locations"
        # ]
        #endregion

        command_text = self.__get_command_text("/_all_dbs")
        req = requests.get(command_text)
        status_code = req.status_code
        result = None

        if status_code == 200:
            result = req.json()
        elif self.__throw_errors is True:
            json_result = json.loads(req.text)
            error = json_result["error"]
            reason = json_result["reason"]
            cdb_error = CouchDBError()
            cdb_error.title = "Unknown status code encountered : " + status_code
            cdb_error.description = "[" + error + "]" + reason
            raise cdb_error

        return result

    def retrieve_database(self, database_name: string=None) -> CouchDB:
        """
        Retrieves the basic information related to a CoucbDB database

        :param database_name: a string representation of the database name in CouchDB to retrieve
        :return: A CoucbDB object if found, None otherwise
        """

        #region Sample Req/Resp
        # GET /receipts HTTP/1.1
        # Accept: application/json
        # Host: localhost:5984

        # HTTP/1.1 200 OK
        # Cache-Control: must-revalidate
        # Content-Length: 258
        # Content-Type: application/json
        # Date: Mon, 12 Aug 2013 01:38:57 GMT
        # Server: CouchDB (Erlang/OTP)
        #
        # {
        #     "committed_update_seq": 292786,
        #     "compact_running": false,
        #     "data_size": 65031503,
        #     "db_name": "receipts",
        #     "disk_format_version": 6,
        #     "disk_size": 137433211,
        #     "doc_count": 6146,
        #     "doc_del_count": 64637,
        #     "instance_start_time": "1376269325408900",
        #     "purge_seq": 0,
        #     "update_seq": 292786
        # }
        #endregion

        command_text = self.__get_command_text("/" + database_name)
        req = requests.get(command_text)
        status_code = req.status_code
        result = None
        json_result = None

        if status_code == 200:
            json_result = req.json()
            result = CouchDB()
            result.committed_update_seq = json_result["committed_update_seq"]
            result.compact_running = json_result["compact_running"]
            result.data_size = json_result["data_size"]
            result.db_name = json_result["db_name"]
            result.disk_format_version = json_result["disk_format_version"]
            result.disk_size = json_result["disk_size"]
            result.doc_count = json_result["doc_count"]
            result.doc_del_count = json_result["doc_del_count"]
            result.instance_start_time = json_result["instance_start_time"]
            result.purge_seq = json_result["purge_seq"]
            result.update_seq = json_result["update_seq"]
        elif self.__throw_errors is True:
            json_result = json.loads(req.text)
            error = json_result["error"]
            reason = json_result["reason"]
            cdb_error = CouchDBError()
            cdb_error.title = "404 Not Found – Requested database not found"
            cdb_error.description = "[" + error + "]" + reason
            raise cdb_error

        return result

    def create_document(self, database_name: string=None, did: string=None, value: object=None) -> CouchDBDocument:
        """
        Creates a document for the given CouchDB database provided

        :param did: The document id if you wish to manually assign the ID to the document
        :param value: The object to store as a document in CoucbDB
        :param database_name: A string representation of the database name in CouchDB
        :return: The value provided as a parameter appended with doc_id and rev_id if either are None then create failed
        """

        #region Sample Req/Resp
        #PUT /somedatabase/some_doc_id HTTP/1.0
        # Content-Length: 245
        # Content-Type: application/json
        #
        # {
        #   "Subject":"I like Plankton",
        #   "Author":"Rusty",
        #   "PostedDate":"2006-08-15T17:30:12-04:00",
        #   "Tags":["plankton", "baseball", "decisions"],
        #   "Body":"I decided today that I don't like baseball. I like plankton."
        # }

        # HTTP/1.1 201 Created
        # Etag: "946B7D1C"
        # Date: Thu, 17 Aug 2006 05:39:28 +0000GMT
        # Content-Type: application/json
        # Connection: close
        #
        # {"ok": true, "id": "some_doc_id", "rev": "946B7D1C"}

        # HTTP/1.1 409 Conflict
        # Date: Thu, 17 Aug 2006 05:39:28 +0000GMT
        # Content-Length: 33
        # Connection: close
        #
        # {"error":"conflict","reason":"Document update conflict."}
        #endregion

        if did is None:
            cdb_uid = self.retrieve_uuid()
        else:
            cdb_uid = did

        result = None
        command_text = self.__get_command_text("/" + database_name + "/" + cdb_uid)
        jsn = json.dumps(value, default=lambda o: o.__dict__, sort_keys=True, indent="\t")
        req = requests.put(command_text, jsn)
        status_code = req.status_code
        json_result = None

        if status_code == 201:

            # 201 Created – Document created and stored on disk
            json_result = req.json()
            result = CouchDBDocument()
            result.json = json_result
            result.id = json_result["id"]
            result.rev = json_result["rev"]

        elif self.__throw_errors is True:

            json_result = json.loads(req.text)
            error = json_result["error"]
            reason = json_result["reason"]

            cdb_error = CouchDBError()
            cdb_error.description = "[" + error + "]" + reason

            if status_code == 202:
                cdb_error.title = "202 Accepted – Document data accepted, but not yet stored on disk"
            elif status_code == 400:
                cdb_error.title = "400 Bad Request – Invalid request body or parameters"
            elif status_code == 401:
                cdb_error.title = "401 Unauthorized – Write privileges required"
            elif status_code == 404:
                cdb_error.title = "404 Not Found – Specified database or document ID doesn’t exists"
            elif status_code == 409:
                cdb_error.title = "409 Conflict – Document with the specified ID already exists or specified revision" \
                                  " is not latest for target document"

            raise cdb_error

        return result

    def retrieve_document(self,
                          database_name: string=None,
                          doc_id: string=None,
                          rev_id: string=None,
                          attachments: bool=False,
                          revisions: bool=False,
                          rev_info: bool=False) -> CouchDBDocument:
        """
        Retrieves a CouchDB document

        :param database_name: A string representation of the name of the CouchDB database name
        :param doc_id: A string representation of the document ID to be retrieved
        :param rev_id: A string representation of hte revision ID to be retrieved for a given document ID
        :param attachments: A boolean representation whether or not to retrieve the attachments for the CouchDBDocument
        :return: Returns a populated CouchDBDocument if found, None otherwise
        """

        #region Sample Req/Resp
        #GET /somedatabase/some_doc_id HTTP/1.0
        #GET /somedatabase/some_doc_id?attachments=true HTTP/1.0
        #GET /somedatabase/some_doc_id?rev=946B7D1C HTTP/1.0

        # HTTP/1.1 200 OK
        # Etag: "946B7D1C"
        # Date: Thu, 17 Aug 2006 05:39:28 +0000GMT
        # Content-Type: application/json
        # Content-Length: 256
        # Connection: close
        #
        # {
        #  "_id":"some_doc_id",
        #  "_rev":"946B7D1C",
        #  "Subject":"I like Plankton",
        #  "Author":"Rusty",
        #  "PostedDate":"2006-08-15T17:30:12Z-04:00",
        #  "Tags":["plankton", "baseball", "decisions"],
        #  "Body":"I decided today that I don't like baseball. I like plankton."
        # }
        #endregion

        result = None
        command_text = self.__get_command_text("/" + database_name + "/" + doc_id)
        payload = {"attachments": attachments, "rev": rev_id}
        req = requests.get(command_text, params=payload)
        status_code = req.status_code

        if status_code == 200:

            json_result = req.json()
            cb_doc = CouchDBDocument()
            cb_doc.id = json_result["_id"]
            cb_doc.rev = json_result["_rev"]
            cb_doc.json = json_result

            if attachments:
                # cb_doc.attachments
                #TODO: add attachments
                pass

            if revisions:
                # cb_doc.revisions
                #TODO: add revisions
                pass

            if rev_info:
                cb_doc.revs_info = self.retrieve_document_revision_info(database_name=database_name, doc_id=doc_id)

            # cb_doc.conflicts
            # cb_doc.deleted
            # cb_doc.deleted_conflicts
            # cb_doc.local_seq

            result = cb_doc

        elif self.__throw_errors is True:

            json_result = json.loads(req.text)
            error = json_result["error"]
            reason = json_result["reason"]

            cdb_error = CouchDBError()
            cdb_error.description = "[" + error + "]" + reason

            if status_code == 304:
                cdb_error.title = "304 Not Modified – Document wasn’t modified since specified revision"
            elif status_code == 400:
                cdb_error.title = "400 Bad Request – The format of the request or revision was invalid"
            elif status_code == 401:
                cdb_error.title = "401 Unauthorized – Read privilege required"
            elif status_code == 404:
                cdb_error.title = "404 Not Found – Document not found"

            raise cdb_error

        return result

    def retrieve_document_revision_info(self, database_name: string=None, doc_id: string=None) -> list:
        """
        Retrieves a documents revision info

        :param database_name: A string representation of the name of the CouchDB database
        :param doc_id: A string representation of the Doc ID of the document within the CouchDB database
        :return: None if no revision info found, otherwise a list of RevisionInfo objects for the given Document
        """

        #region Sample Req/Resp
        #GET /somedatabase/some_doc_id?revs_info=true HTTP/1.0

        # {
        #   "_revs_info": [
        #     {"rev": "3-ffffff", "status": "available"},
        #     {"rev": "2-eeeeee", "status": "missing"},
        #     {"rev": "1-dddddd", "status": "deleted"},
        #   ]
        # }
        #endregion

        result = None
        command_text = self.__get_command_text("/" + database_name + "/" + doc_id)
        payload = {"revs_info": "true"}
        req = requests.get(command_text, params=payload)
        status_code = req.status_code

        if status_code == 200 or status_code == 201:

            json_result = req.json()
            revs_info = json_result["_revs_info"]

            result = list()

            for ri in revs_info:

                current_rev = ri["rev"]
                current_status = ri["status"]

                cri = RevisionInfo()
                cri.rev = current_rev

                if current_status == RevisionInfoStatus.Available.value:
                    cri.status = RevisionInfoStatus.Available
                elif current_status == RevisionInfoStatus.Deleted.value:
                    cri.status = RevisionInfoStatus.Deleted
                elif current_status == RevisionInfoStatus.Missing.value:
                    cri.status = RevisionInfoStatus.Missing
                else:
                    cri.status = RevisionInfoStatus.Unknown

                result.append(cri)

        elif self.__throw_errors is True:
            json_result = json.loads(req.text)
            error = json_result["error"]
            reason = json_result["reason"]

            cdb_error = CouchDBError()
            cdb_error.title = "Unknown error was encountered"
            cdb_error.description = "[" + error + "]" + reason
            raise cdb_error

        return result

    def update_document(self, database_name: string=None, value: CouchDBDocument=None) -> bool:
        """
        Updates an existing CoucbDB document in the database

        :param database_name: A string representation of the database name in CouchDB
        :param value: the CoucbDBDocument to be updated
        :return: True if updated, False otherwise
        """

        #region Sample Req/Resp
        # PUT /somedatabase/some_doc_id HTTP/1.0
        # Content-Length: 245
        # Content-Type: application/json

        # {
        #   "Subject":"I like Plankton",
        #   "Author":"Rusty",
        #   "PostedDate":"2006-08-15T17:30:12-04:00",
        #   "Tags":["plankton", "baseball", "decisions"],
        #   "Body":"I decided today that I don't like baseball. I like plankton."
        # }
        #endregion

        result = False
        command_text = self.__get_command_text("/" + database_name + "/" + value.id)
        req = requests.put(command_text, data=value.json_text)
        status_code = req.status_code

        if status_code == 200 or status_code == 201:
            result = True

        elif self.__throw_errors is True:
            json_result = json.loads(req.text)
            error = json_result["error"]
            reason = json_result["reason"]

            cdb_error = CouchDBError()
            cdb_error.title = "Unknown error was encountered"
            cdb_error.description = "[" + error + "]" + reason
            raise cdb_error

        return result

    def delete_document(self, database_name: string=None, doc_id: string=None, rev_id: string=None) -> bool:
        """
        Deletes a given CoucbDB document based on the doc and rev ID

        :param database_name: A string representation of the name of the database
        :param doc_id: A string representation of the doc id
        :param rev_id: A string representation of the rev id (revision)
        :return: True if deleted, false otherwise
        """

        #region Sample Req/Resp
        # DELETE /somedatabase/some_doc HTTP/1.0
        # If-Match: "1582603387"

        # HTTP/1.1 200 OK
        # Etag: "2839830636"
        # Date: Thu, 17 Aug 2006 05:39:28 +0000GMT
        # Content-Type: application/json
        # Connection: close
        #
        # {"ok":true,"rev":"2839830636"}
        #endregion

        result = False

        command_text = self.__get_command_text("/" + database_name + "/" + doc_id)
        payload = {"rev": rev_id}
        req = requests.delete(command_text, params=payload)
        status_code = req.status_code

        if status_code == 200 or status_code == 201 or status_code == 202:

            result = True

        elif self.__throw_errors is True:

            cdb_error = CouchDBError()

            if status_code == 400:
                cdb_error.title = "400 Bad Request – Invalid request body or parameters"
            elif status_code == 401:
                cdb_error.title = "401 Unauthorized – Write privileges required"
            elif status_code == 404:
                cdb_error.title = "404 Not Found – Specified database or document ID doesn’t exists"
            elif status_code == 409:
                cdb_error.title = "409 Conflict – Specified revision is not the latest for target document"

            raise cdb_error

        return result

    def retrieve_all_documents(self, database_name: string=None) -> list:
        """
        Retrieves all documents in the CouchDB
        :param database_name: A string representation of the CouchDB database name
        :return: Retrieves a list of dictionaries containing every documents key and latest revision in the CouchDB
        """

        #region Sample Req / Resp
        #GET /somedatabase/_all_docs HTTP/1.0

        # HTTP/1.1 200 OK
        # Date: Thu, 17 Aug 2006 05:39:28 +0000GMT
        # Content-Type: application/json
        # Connection: close
        #
        # {
        #   "total_rows": 3, "offset": 0, "rows": [
        #     {"id": "doc1", "key": "doc1", "value": {"rev": "4324BB"}},
        #     {"id": "doc2", "key": "doc2", "value": {"rev":"2441HF"}},
        #     {"id": "doc3", "key": "doc3", "value": {"rev":"74EC24"}}
        #   ]
        # }
        #endregion

        return self.retrieve_all_documents_between(database_name=database_name)

    def retrieve_all_documents_between(self,
                                       database_name: string=None,
                                       start_key: string=None,
                                       end_key: string=None,
                                       descending: bool=None,
                                       limit: int=None) -> list:
        """
        Retrieves all documents based on certain criteria

        :param database_name: A string representation of the database name in CouchDB
        :param start_key: A string representation of the start key of the document in CouchDB
        :param end_key: A string representation of the end key of the document in CouchDB
        :param descending: True to sort descending, false for ascending, Otherwise None for as it comes
        :param limit: An integer setting the limit of documents to return
        :return: Empty list of nothing found, otherwise a list of document ID's and Rev's based on the criteria
        """

        #region Sample Req/Resp
        # GET /somedatabase/_all_docs?startkey="doc2"&limit=2 HTTP/1.0
        # GET /somedatabase/_all_docs?startkey="doc2"&endkey="doc3" HTTP/1.0
        # GET /somedatabase/_all_docs?startkey="doc2"&limit=2&descending=true HTTP/1.0

        # HTTP/1.1 200 OK
        # Date: Thu, 17 Aug 2006 05:39:28 +0000GMT
        # Content-Type: application/json
        # Connection: close
        #
        # {
        #   "total_rows": 3, "offset": 1, "rows": [
        #     {"id": "doc2", "key": "doc2", "value": {"rev":"2441HF"}},
        #     {"id": "doc3", "key": "doc3", "value": {"rev":"74EC24"}}
        #   ]
        # }
        #endregion

        result = list()

        command_text = self.__get_command_text("/" + database_name + "/_all_docs")
        payload = {"startkey": start_key, "endkey": end_key, "descending": descending, "limit": limit}
        req = requests.get(command_text, params=payload)
        status_code = req.status_code

        if status_code == 200:

            json_result = req.json()

            for doc in json_result["rows"]:
                current_id = doc["id"]
                current_rev = doc["value"]["rev"]
                d = dict()
                d["id"] = current_id
                d["rev"] = current_rev
                result.append(d)

        elif self.__throw_errors is True:

            json_result = json.loads(req.text)
            error = json_result["error"]
            reason = json_result["reason"]

            cdb_error = CouchDBError()
            cdb_error.title = "Unknown error was encountered"
            cdb_error.description = "[" + error + "]" + reason

            raise cdb_error

        return result

    def create_document_attachment(self,
                                   database_name: string=None,
                                   doc_id: string=None,
                                   rev_id: string=None,
                                   attachment: object=None,
                                   attachment_name: string=None) -> string:
        """
        Creates an attachment for a given document

        :param database_name: A string representation of the name of the database in CouchDB
        :param doc_id: A string representation of the document id
        :param rev_id: A string representation of the revision id
        :param attachment: The actual attachment contents - generally bytes from a file
        :param attachment_name: A string representation of the filename of the attachment
        :return: None if not created, otherwise the revision id for the document
        """

        #region Sample Req/Resp
        # PUT /somedatabase/document/attachment?rev=123 HTTP/1.0
        # Content-Length: 245
        # Content-Type: image/jpeg
        #
        # <JPEG data>

        # {"ok": true, "id": "document", "rev": "765B7D1C"}
        #endregion

        result = None

        command_text = self.__get_command_text("/" + database_name + "/" + doc_id + "/" + attachment_name)
        payload = {"rev": rev_id}
        req = requests.put(url=command_text, params=payload, data=attachment)
        status_code = req.status_code

        if status_code == 200 or status_code == 201 or status_code == 202:

            json_text = req.text
            json_result = json.loads(json_text)
            result = json_result["rev"]

        elif self.__throw_errors is True:

            json_result = json.loads(req.text)
            error = json_result["error"]
            reason = json_result["reason"]

            cdb_error = CouchDBError()
            cdb_error.description = "[" + error + "]" + reason

            if status_code == 400:
                cdb_error.title = "400 Bad Request – Invalid request body or parameters"
            elif status_code == 401:
                cdb_error.title = "401 Unauthorized – Write privileges required"
            elif status_code == 404:
                cdb_error.title = "404 Not Found – Specified database, document or attachment was not found"
            elif status_code == 409:
                cdb_error.title = "409 Conflict – Document’s revision wasn’t specified or it’s not the latest"
            else:
                cdb_error.title = "Unknown error was encountered"

            raise cdb_error

        return result

    def update_document_attachment(self,
                                   database_name: string=None,
                                   doc_id: string=None,
                                   rev_id: string=None,
                                   attachment: object=None,
                                   attachment_name: string=None) -> string:
        """
        Updates a document attachment within CouchDB
        :param database_name: A string representation of the name of the database within CouchDB
        :param doc_id: A string representation of the document ID of the document within the database
        :param rev_id: A string representation of the revision ID of the document within the database
        :param attachment: The raw bytes of the attachment
        :param attachment_name: A string representation of the
        :return: None if not updated, otherwise the revision id for the document
        """

        #region Sample Req/Resp
        # PUT /somedatabase/document/attachment?rev=765B7D1C HTTP/1.0
        # Content-Length: 245
        # Content-Type: image/jpeg
        #
        # <JPEG data>

        #{"ok": true, "id": "document", "rev": "766FC88G"}
        #endregion

        result = None
        command_text = self.__get_command_text("/" + database_name + "/" + doc_id + "/" + attachment_name)
        payload = {"rev": rev_id}
        req = requests.put(url=command_text, params=payload, data=attachment)
        status_code = req.status_code

        if status_code == 200 or status_code == 201:
            json_text = req.text
            json_result = json.loads(json_text)
            result = json_result["rev"]

        return result

    def delete_document_attachment(self,
                                   database_name: string=None,
                                   doc_id: string=None,
                                   rev_id: string=None,
                                   attachment_name: string=None) -> string:
        """
        Deletes a documents attachment in CouchDB

        :param database_name: A string representation of the database name within CouchDB
        :param doc_id: A string representation of the document ID within CouchDB
        :param rev_id: A string representation of the revision ID associated with the document ID in CouchDB
        :param attachment_name: A string representation of the filename of the attachment
        :return: None if not deleted, otherwise the revision id for the document
        """

        #region Sample Req/Resp
        # DELETE /somedatabase/document/attachment?rev=765B7D1C HTTP/1.0

        # {"ok":true,"id":"document","rev":"519558700"}
        #endregion

        result = None

        command_text = self.__get_command_text("/" + database_name + "/" + doc_id + "/" + attachment_name)
        payload = {"rev": rev_id}
        req = requests.delete(command_text, params=payload)
        status_code = req.status_code
        json_text = req.text
        json_result = json.loads(json_text)

        if status_code == 200 or status_code == 201:

            result = json_result["rev"]

        elif self.__throw_errors is True:

            error = json_result["error"]
            reason = json_result["reason"]

            cdb_error = CouchDBError()
            cdb_error.description = "[" + error + "]" + reason

            if status_code == 400:
                cdb_error.title = "400 Bad Request – Invalid request body or parameters"
            elif status_code == 401:
                cdb_error.title = "401 Unauthorized – Write privileges required"
            elif status_code == 404:
                cdb_error.title = "404 Not Found – Specified database, document or attachment was not found"
            elif status_code == 409:
                cdb_error.title = "409 Conflict – Document’s revision wasn’t specified or it’s not the latest"
            else:
                cdb_error.title = "Unknown error was encountered"

            raise cdb_error

        return result

    def retrieve_document_attachment(self,
                                     database_name: string=None,
                                     doc_id: string=None,
                                     rev_id: string=None,
                                     attachment_name: string=None) -> CouchDBDocument:
        """
        Retrieves a document attachment from the CouchDB server

        :param database_name: A string representation of the name of the database in CouchDB
        :param doc_id: A string representation of the document ID in the CouchDB database
        :param rev_id: A string representation of the revision ID related to the document ID in CouchDB
        :param attachment_name: A string representation of the filename of the attachment associated to the document
        :return: A CouchDBDocument object containing the attachment, doc id and rev id
        """

        #region Sample Req/Resp
        #GET /somedatabase/document/attachment HTTP/1.0

        # Content-Type:image/jpeg
        #
        # <JPEG data>
        #endregion

        result = None

        command_text = self.__get_command_text("/" + database_name + "/" + doc_id + "/" + attachment_name)
        payload = {"rev": rev_id}
        req = requests.get(command_text, params=payload)
        status_code = req.status_code

        if status_code == 200 or status_code == 201:

            result = CouchDBDocument()
            result.id = doc_id
            result.rev = rev_id
            result.attachments = list()
            result.attachments.append(req.content)

        elif self.__throw_errors is True:

            json_result = json.loads(req.text)
            error = json_result["error"]
            reason = json_result["reason"]

            cdb_error = CouchDBError()
            cdb_error.description = "[" + error + "]" + reason

            if status_code == 304:
                cdb_error.title = "304 Not Modified – Attachment wasn’t modified if ETag equals specified " \
                                  "If-None-Match header"
            elif status_code == 401:
                cdb_error.title = "401 Unauthorized – Read privilege required"
            elif status_code == 404:
                cdb_error.title = "404 Not Found – Specified database, document or attachment was not found"

            raise cdb_error

        return result