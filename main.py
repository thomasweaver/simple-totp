from flask import Flask, jsonify, abort
import pyotp, datetime, google
from urllib.parse import quote_plus
from google.cloud import secretmanager

app = Flask(__name__)
project_id = "sandpit-hub"

client = secretmanager.SecretManagerServiceClient()
# Build the parent name from the project.
parent = f"projects/{project_id}"


def get_secret(name):
    #projects/*/secrets/*/versions/latest
    secret_path = f"{parent}/secrets/{name}/versions/latest"
    try:
        response = client.access_secret_version(request={"name": secret_path})
    except google.api_core.exceptions.NotFound:
        abort(404)
    return response.payload.data.decode("UTF-8")


@app.route('/otp/<id>', methods=['GET'])
def get_otp(id):
    #print(id)
    # Create a TOTP object with the secret seed string
    secret_uri = get_secret(quote_plus(id))
    print(secret_uri)
    try:
        totp = pyotp.parse_uri(secret_uri)
    except Exception:
        return "Error generating TOTP"
    time_remaining = totp.interval - datetime.datetime.now().timestamp() % totp.interval
    # Generate the current one-time password
    otp = totp.now()
    # Return the OTP as a JSON response
    return jsonify({'otp': otp, 'time_remaining': time_remaining})

if __name__ == '__main__':
    app.run(debug=True)
