NR_NODES=1

VERSION=0.0.0.1
APP_NAME={{cookiecutter.app_name}}
CLUSTER_NAME={{cookiecutter.google_cloud_cluster_name}}
GCLOUD_PROJECT={{cookiecutter.google_cloud_project}}
GCLOUD_CONFIGURATION={{cookiecutter.google_cloud_configuration}}
ZONE={{cookiecutter.google_cloud_zone}}
MACHINE_TYPE={{cookiecutter.machine_type}} # see https://cloud.google.com/compute/docs/machine-types

# set ALEXA_APPLICATION_ID if it's not set, add to your environment variables to not commit it
ALEXA_APPLICATION_ID ?= "{{cookiecutter.application_id}}"

TLS_KEY={{cookiecutter.tls_key}}
TLS_CERTIFICATE={{cookiecutter.tls_certificate}}

DOCKER_TAG:=gcr.io/$(GCLOUD_PROJECT)/$(APP_NAME):$(VERSION)

.PHONY: all
all: update


.PHONY: clean
clean:
	find . -name '*.pyc' -delete


.PHONY: deploy
deploy: push template secrets update


.PHONY: update
update: push template
	kubectl apply -f kubernetes_configs/backend.yaml --record


.PHONY: create-cluster
create-cluster:
	gcloud container clusters create $(CLUSTER_NAME) \
		--scopes "cloud-platform" \
		--num-nodes=$(NR_NODES) \
		--zone=$(ZONE) \
		--machine-type=$(MACHINE_TYPE) \
		--project=$(GCLOUD_PROJECT) \
		--configuration=$(GCLOUD_CONFIGURATION)
	# configure kubectl to talk to the cluster.
	gcloud container clusters get-credentials $(CLUSTER_NAME) \
		--project=$(GCLOUD_PROJECT) \
		--configuration=$(GCLOUD_CONFIGURATION)


.PHONY: delete-deployments
delete-deployments:
	kubectl delete -f kubernetes_configs/backend.yaml
	kubectl delete secret tls-secret


.PHONY: delete-cluster
delete-cluster:
	gcloud container clusters delete $(CLUSTER_NAME) \
		--project=$(GCLOUD_PROJECT) \
		--configuration=$(GCLOUD_CONFIGURATION)


.PHONY: delete-project
delete-project: delete-cluster
	gcloud projects delete $(GCLOUD_PROJECT)


.PHONY: template
template:
	# need to quote / special chars
	sed "s/\$$DOCKER_TAG/$(subst /,\/,$(DOCKER_TAG))/g" kubernetes_configs/backend_abstract.yaml > kubernetes_configs/backend.yaml
	sed -i "s/\$$APPLICATION_ID/$(ALEXA_APPLICATION_ID)/g" kubernetes_configs/backend.yaml


.PHONY: secrets
secrets:
	kubectl create secret tls tls-secret --key=$(TLS_KEY) --cert=$(TLS_CERTIFICATE)


.PHONY: build
build:
	docker build -t $(DOCKER_TAG) bot/


.PHONY: push
push:
	gcloud \
		--project=$(GCLOUD_PROJECT) \
		--configuration=$(GCLOUD_CONFIGURATION) \
		docker -- push $(DOCKER_TAG)


.PHONY: run-local
run-local:
	docker run -p 8088:8088 --rm -it $(DOCKER_TAG)


.PHONY: test
test:
	cd bot && py.test


.PHONY: test-code-quality
test-code-quality:
	py.test --cov-config bot/.coveragerc --cov=bot
	# there are always style issues --> avoid exiting with error
	pycodestyle --statistics --format=pylint --max-line-length=130 bot/ || exit 0
