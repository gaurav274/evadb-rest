docker build --tag evadb-rest-image .
docker tag evadb-rest-image evadbRestDocker.azurecr.io/evadb-rest-image:latest
docker push evadbRestDocker.azurecr.io/evadb-rest-image:latest
