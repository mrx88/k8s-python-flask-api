# Introduction
Example for setting up Python API using Flask on Kubernetes

# Requirements
* Python 3.7 and Flask (check requirements.txt for versions)
* [Pipenv](https://github.com/pypa/pipenv) (version 2018.11.26) virtual environment for python development
* [Helm](https://helm.sh/) for nginx ingress chart deployment (HelmV2 with Tiller used in this case, but consider using helmv3 without tiller)

# Set up Python development environment

```
# Set up python virtual environment using pipenv:
pipenv --three --python=`which python3.7`
pipenv shell

# Install Flask
pipenv install Flask

# Lock dependencies
pipenv lock

# requirements.txt for Dockerfile
pipenv run pip freeze > requirements.txt

# Validate
pipenv check
Checking PEP 508 requirements…
Passed!
Checking installed package safety…
All good!
```

# Test application locally:

```
# Flask dev server settings
export FLASK_ENV=development
export FLASK_APP=app.py

flask run
 * Serving Flask app "app.py" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 210-079-390

# Test the / endpoint
 curl http://localhost:5000/    
Success!   

# Test the /ping endpoint
 curl http://localhost:5000/ping
Ok   

# Flask dev server logs:
127.0.0.1 - - [28/Jan/2020 14:05:55] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [28/Jan/2020 14:07:50] "GET /ping HTTP/1.1" 200 -

# Validate syntax 
pipenv check
Checking PEP 508 requirements…
Passed!
Checking installed package safety…
All good!
```

# Build Docker image

Using official python 3.7 image for Debian Buster (slim version)

```
docker build --rm -f "Dockerfile" -t k8s-flaskapi:latest "."

...
Successfully built 2fdb0c613a33
Successfully tagged k8s-flaskapi:latest
```

# Setting up K8s cluster

For local development it is possible to use [Minikube](https://kubernetes.io/docs/setup/learning-environment/minikube/) or [Kind](https://kind.sigs.k8s.io/).
I have used my own remote Azure Kubernetes Service (AKS) cluster deployed with terraform:
https://github.com/mrx88/terraform-aks-azure


# Deployment

```
# Push the Docker image to Docker Registry
docker login -u acrdev88registry -p "${DOCKER_REGISTRY_PW}" acrdev88registry.azurecr.io
docker tag k8s-flaskapi:latest acrdev88registry.azurecr.io/k8s-flaskapi:latest
docker push acrdev88registry.azurecr.io/k8s-flaskapi:latest

# Use Helm for deploying nginx-ingress
helm install stable/nginx-ingress --namespace ingress-flaskapi --set controller.replicaCount=2 --set service.annotations[0]="service.beta.kubernetes.io/azure-dns-label-name: flaskapi.westeurope.cloudapp.azure.com"

# Deploy K8s manifest
kubectl apply -f k8s/deployment.yaml

# Check if application pods are running
kubectl get pods |grep flask                  
flaskapi-84df6444c4-n7vzp                         1/1     Running   0          59s
flaskapi-84df6444c4-vr4f7                         1/1     Running   0          59s
flaskapi-84df6444c4-zhb2l                         1/1     Running   0          59s

# Get service IP
kubectl get svc |grep flask
flaskapi                  ClusterIP   10.0.1.53     <none>        80/TCP    2m50s

# Check if nginx controller pods are running
kubectl get pods --namespace ingress-flaskapi
NAME                                                           READY   STATUS    RESTARTS   AGE
killjoy-dingo-nginx-ingress-controller-554cd88c77-ttd8v        1/1     Running   0          8m5s
killjoy-dingo-nginx-ingress-controller-554cd88c77-xf7wb        1/1     Running   0          8m5s
killjoy-dingo-nginx-ingress-default-backend-8465d5459b-brdk2   1/1     Running   0          8m5s

# Get nginx ingress 
kubectl get ingress |grep flask
flaskapi-nginx          flaskapi.westeurope.cloudapp.azure.com                    80        2m43s

# Test
curl flaskapi.westeurope.cloudapp.azure.com/
Success!                                                                                        

curl flaskapi.westeurope.cloudapp.azure.com/ping
Ok    

# Verify if request reached nginx ingress
kubectl logs killjoy-dingo-nginx-ingress-controller-554cd88c77-ttd8v -n ingress-flaskapi | tail -1
10.244.0.1 - - [28/Jan/2020:14:31:35 +0000] "GET /ping HTTP/1.1" 200 2 "-" "curl/7.52.1" 106 0.043 [prod-flaskapi-80] [] 10.244.0.3:5000 2 0.044 200 ce48d112c8b46d2b6b80a753952fb611                                                                                        
```
