"""Endpoints and functions concerning commands run in external processes."""
import json

import redis
from flask import jsonify, Blueprint

async_commands = Blueprint("async_commands", __name__)

@async_commands.route("/state/<command_id>")
def command_state(command_id):
    with redis.Redis(decode_responses=True) as rconn:
        state = rconn.hgetall(name=command_id)
        if not state:
            return jsonify(
                status=404,
                error="The command id provided does not exist.")
        state = {key: val for key,val in state.items()}
        return jsonify(state)
