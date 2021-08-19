.DEFAULT_GOAL := help

IMAGE_TAG := "ssh-port-forward-client"

build: ## build the image
	docker build . -t ${IMAGE_TAG}

buildx: ## build & push the image with docker buildx
	docker buildx build . --file=./Dockerfile \
		--platform=${ARCH} \
		--tag=${IMAGE_TAG} \
		--output type=image,push=true

start: ## start existing container
	docker start ${IMAGE_TAG}

stop: ## stop existing container
	docker stop ${IMAGE_TAG}

rm: ## remove existing container
	docker rm ${IMAGE_TAG}

attach-it: ## attach to existing container on interactive mode
	docker exec -it ${IMAGE_TAG} bash

help: ## show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
