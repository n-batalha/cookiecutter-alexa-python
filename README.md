# Cookiecutter Alexa Skill in Python, with Kubernetes

## Intro

This is an example of an Alexa skill, written in Python (via [Alexandra](https://github.com/erik/alexandra)) and 
deployed via a Kubernetes cluster on the Google Cloud. 

There is a lot to do but it's a convenient starting point for those wanting to develop Alexa skills with this stack.

### Features

 * deployment code for starting a service in minutes
 * examples of the Alexa API calls
 * test examples
 * basic logging
 * coverage test and pep8 checks

## Setup

### Requirements

* [cookiecutter](https://cookiecutter.readthedocs.io/)
* [Google Cloud SDK](https://cloud.google.com/sdk/) with `kubectl`.
* [Docker](https://www.docker.com/)
* A Google Cloud project
* A certificate and private key for TLS/SSL support (see below)

#### TLS certificate

For the TLS/SSL support (compulsory in Alexa), you need a private key and certificate. 
You can make a self-signed one for testing only, with:

```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /tmp/tls.key -out /tmp/tls.crt -subj "/CN=foobar.com"
```

Note that you must replace `foobar.com` with the actual domain that you will use.

### Installation

1. Configure a skill on your Amazon dev account (not yet configurable programmatically) adding the certificate `tls.crt` created above, your domain and desired endpoint (e.g. `/myskill`);
2. Take note of the application ID given by Amazon (something like `amzn1.echo-sdk-ams.app.xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxx`);
3. Prepare your project with:

```
cookiecutter <this_repo_url>
```

You will be asked to select a number of parameters. The main ones are:

```
google_cloud_project: your Google Cloud project name
google_cloud_configuration: normally 'default' suffices
tls_key: (e.g /tmp/key.pem)
tls_certificate (e.g /tmp/tls.crt)
endpoint: (/myendpoint)
application_id: (e.g amzn1.echo-sdk-ams.app.xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxx)
```

You now have a directory with your project, under `{project_slug}` (selected above). This will be your root folder. 

### Running locally (without Docker)

Configure the environment locally first with 

```
mkvirtualenv <env_name>
pip install -U pip
pip install -r requirements.txt
```

And then run 

```
python bot/bot/app.py
```

### Local (with Docker)

```
make build
make run-local
```

Note that this will run the production app, with data validation, so local test calls will get a `403`. 
See the [FAQs](FAQ.md).

### Deployment

1. In the Alexa Skills page of your new skill configured above, add the assets available under `speech_assets` to their respective fields:
 * `intent_schema.json`
 * `sample_utterances.txt`
 * `custom_slot_types`
2. Run 

```
make build
make create-cluster
make deploy
```

3. configure a domain to point the DNS record of type `A` and name `@` to the ip given to your cluster.
You can retrieve it with `kubectl get ing gce-ingress` (give it a few minutes after running the deployment, 
for the pods to become available).

## Updates

For updates in the code, update the version in the `Makefile` and run:

```
make build && make update
```

Note that:

>a Deployment’s rollout is triggered if and only if the Deployment’s pod template (i.e. .spec.template) is changed, e.g. updating labels or container images of the template. Other updates, such as scaling the Deployment, will not trigger a rollout.

From [Kubernetes User Guide - Deployments](http://kubernetes.io/docs/user-guide/deployments/).

## Tests

For the test suite:

```
make test
``` 

To run tests manually, with the local setup above, you can start a local test server with:

```
python bot/bot/app.py
```

You can test the `LaunchIntent` with (replace `APPLICATION_ID`):

```
curl -v -k http://localhost:8088/ -H "Content-Type: application/json" --data-binary '{
  "version": "1.0",
  "session": {
    "new": true,
    "sessionId": "session1234",
    "application": {
      "applicationId": "APPLICATION_ID"
    },
    "attributes": {},
    "user": {
      "userId": null
    }
  },
  "request": {
    "type": "LaunchRequest",
    "requestId": "request5678",
    "timestamp": "2016-07-03T17:23:58Z"
  }
}'
```

In our case, it would return a result with:

```
"outputSpeech": {
    "text": "Which ingredient would you like to replace?", 
    "type": "PlainText"
}
```

## Logging

For now, these are reported in the Kubernetes dashboard pod logs only.

## FAQ's

See [the main doc](FAQ.md).
