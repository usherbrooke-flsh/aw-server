from typing import List, Dict
from datetime import datetime
import binascii
import os

from flask import request
from flask_restplus import Api, Resource, fields

from . import app, logger


# SECURITY
# As we work our way through features, disable (while this is False, we should only accept connections from localhost)
SECURITY_ENABLED = False

# For the planned zeroknowledge storage feature
ZEROKNOWLEDGE_ENABLED = False


api = Api(app)

@api.route("/api/0/buckets")
class BucketsResource(Resource):
    """
    Used to list buckets.
    """

    def get(self, bucket_id):
        logger.debug("Received get request for bucket '{}'".format(bucket_id))
        return app.db[bucket_id].metadata()

@api.route("/api/0/buckets/<string:bucket_id>")
class BucketResource(Resource):
    """
    Used to get metadata about buckets and create them.
    """

    def get(self, bucket_id):
        logger.debug("Received get request for bucket '{}'".format(bucket_id))
        return app.db[bucket_id].metadata()

    def post(self, bucket_id):
        # TODO: Implement bucket creation
        raise NotImplementedError


@api.route("/api/0/buckets/<string:bucket_id>/events")
class EventResource(Resource):
    """
    Used to get and create events in a particular bucket.
    """

    def get(self, bucket_id):
        logger.debug("Received get request for events in bucket '{}'".format(bucket_id))
        return app.db[bucket_id].get()

    def post(self, bucket_id):
        logger.debug("Received post request for event in bucket '{}' and data: {}".format(bucket_id, request.get_json()))
        data = request.get_json()
        if isinstance(data, dict):
            app.db[bucket_id].insert(data)
        elif isinstance(data, list):
            for event in data:
                app.db[bucket_id].insert(event)
        else:
            logger.error("Invalid JSON object")
            return {}, 500
        return {}, 200


heartbeats = {}   # type: Dict[str, datetime]


@api.route("/api/0/heartbeat/<string:session_id>")
class HeartbeatResource(Resource):
    """
    WIP!

    Used to give clients the ability to signal on regular intervals something particular which can then be post-processed into events.
    The endpoint could compress a list of events which only differ by their timestamps into a event with a list of the timestamps.

    Should store the last time time the client checked in.
    """

    def get(self, client_name):
        logger.debug("Received heartbeat status request for client '{}'".format(client_name))
        if client_name in heartbeats:
            return heartbeats[client_name].isoformat()
        else:
            return "No heartbeat has been received for this client"

    def post(self, client_name):
        logger.debug("Received heartbeat for client '{}'".format(client_name))
        heartbeats[client_name] = datetime.now()
        return "success", 200
