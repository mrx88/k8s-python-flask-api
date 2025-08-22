# Introduction
Example for setting up Python API using Flask on Kubernetes (Modernized)

# Requirements
* Python 3.12 and Flask (check requirements.txt for versions)
* [Pipenv](https://github.com/pypa/pipenv) virtual environment for python development
* [Helm](https://helm.sh/) for nginx ingress chart deployment (Helm v3 recommended)
* Docker for containerization
* Kubernetes cluster for deployment

# Set up Python development environment

```bash
# Set up python virtual environment using pipenv:
pipenv --python=`which python3.12`
pipenv shell

# Install dependencies
pipenv install Flask

# Install development dependencies
pipenv install --dev

# Lock dependencies
pipenv lock

# requirements.txt for Dockerfile
pipenv requirements > requirements.txt

# Validate code quality
pipenv run flake8 app.py
pipenv run pylint app.py

# Run tests
pipenv run pytest
```

# Test application locally:

```bash
# Flask dev server settings (development)
export FLASK_ENV=development
export FLASK_DEBUG=true
export FLASK_APP=app.py

# Or run directly
python app.py

# The application will start on http://0.0.0.0:5000/

# Test the / endpoint (JSON response)
curl http://localhost:5000/
{"message": "Success!", "status": "ok"}

# Test the /ping endpoint (JSON response)  
curl http://localhost:5000/ping
{"message": "Ok", "status": "healthy"}

# Test the /health endpoint (for Kubernetes health checks)
curl http://localhost:5000/health
{"service": "flask-api", "status": "healthy", "version": "1.0.0"}

# Run tests
pytest -v

# Validate code quality
flake8 app.py
```

# Build Docker image

Using official Python 3.12 image for Debian Bookworm (slim version) with security improvements

```bash
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
