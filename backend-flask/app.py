import os
import sys

from flask import Flask
from flask import request, g
from flask_cors import CORS, cross_origin

from aws_xray_sdk.core import xray_recorder

from lib.rollbar import init_rollbar
from lib.xray import init_xray
from lib.cors import init_cors
from lib.cloudwatch import init_cloudwatch
from lib.honeycomb import init_honeycomb
from lib.cognito_jwt_token import jwt_required
from lib.helpers import model_json

from services.home_activities import *
from services.notifications_activities import *
from services.user_activities import *
from services.create_activity import *
from services.create_reply import *
from services.search_activities import *
from services.message_groups import *
from services.messages import *
from services.create_message import *
from services.show_activity import *
from services.users_short import *
from services.update_profile import *

# OTEL - Show this in the logs within the backend-flask app (STDOUT)
#simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
#provider.add_span_processor(simple_processor)
#trace.set_tracer_provider(provider)
#tracer = trace.get_tracer(__name__)

app = Flask(__name__)

## initalization --------
init_xray(app)
init_honeycomb(app)
init_cors(app)
with app.app_context():
  g.rollbar = init_rollbar(app)


#@app.route('/rollbar/test')
#def rollbar_test():
#    rollbar.report_message('Hello World!', 'warning')
#    return "Hello World!"

@app.route('/api/health-check')
def health_check():
  return {'success': True, 'ver': 1}, 200
    
@app.route("/api/message_groups", methods=['GET'])
@jwt_required()
def data_message_groups():
  model = MessageGroups.run(cognito_user_id=g.cognito_user_id)
  return model_json(model)

@app.route("/api/messages/<string:message_group_uuid>", methods=['GET'])
@jwt_required()
def data_messages(message_group_uuid):
  model = Messages.run(
      cognito_user_id=g.cognito_user_id,
      message_group_uuid=message_group_uuid
    )
  return model_json(model)

@app.route("/api/messages", methods=['POST','OPTIONS'])
@cross_origin()
@jwt_required()
def data_create_message():
  if message_group_uuid == None:
    # Create for the first time
    model = CreateMessage.run(
      mode="create",
      message=message,
      cognito_user_id=g.cognito_user_id,
      user_receiver_handle=user_receiver_handle
    )
  else:
    # Push onto existing Message Group
    model = CreateMessage.run(
      mode="update",
      message=message,
      message_group_uuid=message_group_uuid,
      cognito_user_id=g.cognito_user_id
    )
  return model_json(model)

def default_home_feed(e):
  # unauthenicatied request
  app.logger.debug(e)
  app.logger.debug("unauthenicated")
  data = HomeActivities.run()
  return data, 200

@app.route("/api/activities/home", methods=['GET'])
@xray_recorder.capture('activities_home')
@jwt_required(on_error=default_home_feed)
def data_home():
  data = HomeActivities.run(cognito_user_id=g.cognito_user_id)
  return data, 200

@app.route("/api/activities/notifications", methods=['GET'])
def data_notifications():
  print("* DEBUG Notifications: 1")
  data = NotificationsActivities.run()
  print("* DEBUG Notifications: 4")
  return data, 200

@app.route("/api/activities/@<string:handle>", methods=['GET'])
@xray_recorder.capture('activities_users')
def data_handle(handle):
  model = UserActivities.run(handle)
  return return_model(model)

@app.route("/api/activities/search", methods=['GET'])
def data_search():
  term = request.args.get('term')
  model = SearchActivities.run(term)
  return model_json(model)

@app.route("/api/activities", methods=['POST','OPTIONS'])
@cross_origin()
@jwt_required()
def data_activities():
  message = request.json['message']
  ttl = request.json['ttl']
  model = CreateActivity.run(message, g.cognito_user_id, ttl)
  return model_json(model)

@app.route("/api/activities/<string:activity_uuid>", methods=['GET'])
@xray_recorder.capture('activities_show')
def data_show_activity(activity_uuid):
  data = ShowActivity.run(activity_uuid=activity_uuid)
  return data, 200

@app.route("/api/activities/<string:activity_uuid>/reply", methods=['POST','OPTIONS'])
@cross_origin()
def data_activities_reply(activity_uuid):
  user_handle  = 'andrewbrown'
  message = request.json['message']
  model = CreateReply.run(message, user_handle, activity_uuid)
  return model_json(model)

@app.route("/api/users/@<string:handle>/short", methods=['GET'])
def data_users_short(handle):
  data = UsersShort.run(handle)
  return data, 200

@app.route("/api/profile/update", methods=['POST','OPTIONS'])
@cross_origin()
@jwt_required()
def data_update_profile():
  bio          = request.json.get('bio',None)
  display_name = request.json.get('display_name',None)
  model = UpdateProfile.run(
    cognito_user_id=g.cognito_user_id,
    bio=bio,
    display_name=display_name
  )
  return model_json(model)
  
    
if __name__ == "__main__":
  app.run(debug=True)