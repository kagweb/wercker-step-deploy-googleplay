#!/usr/bin/python

import argparse
import sys
from apiclient import sample_tools
from oauth2client import client

# Declare command-line flags.
argparser = argparse.ArgumentParser(description='Upload Android app to Google Play.')
argparser.add_argument('service_account_email',
                       help='EXAMPLE@developer.gserviceaccount.com')
argparser.add_argument('key_file',
                       help='The path to the Key file.')
argparser.add_argument('package_name',
                       help='The package name. Example: com.android.sample')
argparser.add_argument('apk_file',
                       help='The path to the APK file to upload.')
argparser.add_argument('track',
                       nargs='?',
                       default='alpha',
                       help='Can be \'alpha\', \'beta\', \'production\' or \'rollout\'')

def main(argv):
  flags = argparser.parse_args()

  # Process flags and read their values.
  service_account_email = flags.service_account_email
  key_file = flags.key_file
  package_name = flags.package_name
  apk_file = flags.apk_file
  track = flags.track

  f = file(key_file, 'rb')
  key = f.read()
  f.close()

  credentials = client.SignedJwtAssertionCredentials(
      service_account_email,
      key,
      scope='https://www.googleapis.com/auth/androidpublisher')
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build('androidpublisher', 'v2', http=http)


  try:
    edit_request = service.edits().insert(body={}, packageName=package_name)
    result = edit_request.execute()
    edit_id = result['id']

    apk_response = service.edits().apks().upload(
        editId=edit_id,
        packageName=package_name,
        media_body=apk_file).execute()

    print 'Version code %d has been uploaded' % apk_response['versionCode']

    track_response = service.edits().tracks().update(
        editId=edit_id,
        track=track,
        packageName=package_name,
        body={u'versionCodes': [apk_response['versionCode']]}).execute()

    print 'Track %s is set for version code(s) %s' % (
        track_response['track'], str(track_response['versionCodes']))

    commit_request = service.edits().commit(
        editId=edit_id, packageName=package_name).execute()

    print 'Edit "%s" has been committed' % (commit_request['id'])

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
    main(sys.argv)
