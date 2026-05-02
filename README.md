# Securing Microservices and Containers
## Course / Assignment
**Course:** Security Fundamentals for Cloud  
**Module:** Securing Microservices and Containers  
**Topic:** Develop a microservices application and secure container infrastructure
## Objective
The objective of this assignment is to develop a small microservices-based application, containerize the services using Docker, scan the container images for vulnerabilities using Trivy, and deploy the services on a Kubernetes cluster with security controls such as Kubernetes Secrets, NetworkPolicy, resource limits, and container `securityContext`.
## Microservices Implemented
This project contains two microservices:
| Service | Description | Port | Main Endpoints |
|---|---|---:|---|
| `auth-service` | Authentication-related service | 8081 | `/`, `/health`, `/login` |
| `product-service` | Product-related service | 8082 | `/`, `/health`, `/products` |
## Tools Used
| Tool | Purpose |
|---|---|
| Docker | Containerization of microservices |
| Trivy | Container image vulnerability scanning |
| Amazon ECR | Container image registry |
| Amazon EKS | Kubernetes cluster |
| Kubernetes | Deployment and orchestration |
| Helm | Packaging and redeployment of Kubernetes manifests |
| AWS CloudShell | Development and execution environment |
## High-Level Architecture
```text
                 +-----------------------------+
                 |        AWS CloudShell        |
                 |  Docker / Trivy / kubectl   |
                 |           Helm              |
                 +--------------+--------------+
                                |
                                v
                 +-----------------------------+
                 |        Amazon ECR           |
                 |  auth-service:v1            |
                 |  product-service:v1         |
                 +--------------+--------------+
                                |
                                v
+------------------------------------------------------------------+
|                         Amazon EKS Cluster                       |
|                                                                  |
|  Namespace: microservices-secure-ns                              |
|                                                                  |
|   +------------------------+        +------------------------+    |
|   |   auth-service          |        |   product-service      |    |
|   |   Deployment            |        |   Deployment           |    |
|   |   Replicas: 2           |        |   Replicas: 2          |    |
|   |   Port: 8081            |        |   Port: 8082           |    |
|   +-----------+------------+        +-----------+------------+    |
|               |                                 |                 |
|               v                                 v                 |
|   +------------------------+        +------------------------+    |
|   | auth-service Service   |        | product-service Service|    |
|   | ClusterIP              |        | ClusterIP              |    |
|   +------------------------+        +------------------------+    |
|                                                                  |
|   +----------------------------------------------------------+   |
|   | Kubernetes Secret: app-secret                            |   |
|   | APP_ENV, AUTH_TOKEN                                      |   |
|   +----------------------------------------------------------+   |
|                                                                  |
|   +----------------------------------------------------------+   |
|   | NetworkPolicy: restrict-microservice-traffic             |   |
|   | Allows controlled pod-to-pod internal traffic             |   |
|   +----------------------------------------------------------+   |
+------------------------------------------------------------------+

Repository Structure

.
├── README.md
├── assignment/
│   └── Securing_Microservices_and_Containers_Assignment.docx
├── auth-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── product-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── k8s/
│   ├── namespace.yaml
│   ├── secret.yaml
│   ├── auth-deployment.yaml
│   ├── product-deployment.yaml
│   └── networkpolicy.yaml
├── helm/
│   └── microservices-secure-chart/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── namespace.yaml
│           ├── secret.yaml
│           ├── auth-deployment.yaml
│           ├── product-deployment.yaml
│           └── networkpolicy.yaml
├── reports/
│   ├── trivy-auth-service.txt
│   ├── trivy-product-service.txt
│   └── trivy-scan-before.txt
└── commands/
    └── cloudshell-command-history.txt

Implementation Steps

1. Create Microservices

Two Flask-based microservices were created:

* auth-service
* product-service

Each service contains:

* app.py
* requirements.txt
* Dockerfile

2. Build Docker Images

docker build -t auth-service:v1 ./auth-service
docker build -t product-service:v1 ./product-service

Verify images:

docker images | grep service

3. Test Docker Containers Locally

docker run -d -p 8081:8081 --name auth-service auth-service:v1
docker run -d -p 8082:8082 --name product-service product-service:v1

Test endpoints:

curl http://localhost:8081/
curl http://localhost:8081/health
curl -X POST http://localhost:8081/login
curl http://localhost:8082/
curl http://localhost:8082/health
curl http://localhost:8082/products

4. Scan Images Using Trivy

Trivy was used to perform vulnerability assessment of the container images.

docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /tmp/trivy-cache:/root/.cache/ \
  aquasec/trivy:latest image auth-service:v1 > trivy-auth-service.txt
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /tmp/trivy-cache:/root/.cache/ \
  aquasec/trivy:latest image product-service:v1 > trivy-product-service.txt

The reports are stored in the reports/ folder.

5. Push Images to Amazon ECR

aws ecr create-repository --repository-name auth-service --region ap-south-1
aws ecr create-repository --repository-name product-service --region ap-south-1

Login to ECR:

aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com

Tag and push:

docker tag auth-service:v1 <account-id>.dkr.ecr.ap-south-1.amazonaws.com/auth-service:v1
docker tag product-service:v1 <account-id>.dkr.ecr.ap-south-1.amazonaws.com/product-service:v1
docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/auth-service:v1
docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/product-service:v1

6. Deploy on Amazon EKS

Update kubeconfig:

aws eks update-kubeconfig --region ap-south-1 --name microservices-secure

Verify nodes:

kubectl get nodes

Apply raw Kubernetes manifests:

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/auth-deployment.yaml
kubectl apply -f k8s/product-deployment.yaml
kubectl apply -f k8s/networkpolicy.yaml

Verify deployment:

kubectl get all -n microservices-secure-ns

7. Kubernetes Secrets

A Kubernetes Secret named app-secret was created to store application configuration values.

kubectl get secrets -n microservices-secure-ns
kubectl describe secret app-secret -n microservices-secure-ns

8. Kubernetes NetworkPolicy

A NetworkPolicy named restrict-microservice-traffic was created to restrict ingress traffic within the namespace.

kubectl get networkpolicy -n microservices-secure-ns
kubectl describe networkpolicy restrict-microservice-traffic -n microservices-secure-ns

9. Container Security Hardening

The deployments include container-level security controls using securityContext.

Security controls used:

* Run as non-root user
* Disable privilege escalation
* Drop Linux capabilities
* Define CPU and memory requests/limits

Example:

securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL

10. Helm Deployment

Helm was used to package and redeploy the Kubernetes manifests.

Install Helm:

curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
helm version

Create chart:

helm create microservices-secure-chart

Lint chart:

helm lint microservices-secure-chart

Deploy using Helm:

helm install microservices-secure-release ./microservices-secure-chart

Verify Helm deployment:

helm list
helm status microservices-secure-release
kubectl get all -n microservices-secure-ns

Application Testing in Kubernetes

A temporary curl pod was used to test the deployed services from inside the Kubernetes cluster.

kubectl run test-client --rm -it --image=curlimages/curl -n microservices-secure-ns -- sh

Inside the test pod:

curl http://auth-service/
curl http://auth-service/health
curl -X POST http://auth-service/login
curl http://product-service/
curl http://product-service/health
curl http://product-service/products

Expected outputs:

{"service":"auth-service","status":"running"}
{"status":"healthy"}
{"message":"User authenticated successfully"}
{"service":"product-service","status":"running"}
{"status":"healthy"}
{"products":[{"id":1,"name":"Laptop"},{"id":2,"name":"Mobile"}]}

Requirement Coverage

Assignment Requirement	Status
Create 2–3 microservices	Completed
Authentication service	Completed
Product service	Completed
Containerize services using Docker	Completed
Build Docker images	Completed
Scan container images using Trivy	Completed
Perform vulnerability assessment	Completed
Deploy application in Kubernetes cluster	Completed
Implement Kubernetes Network Policies	Completed
Store secrets using Kubernetes Secrets	Completed
Use Helm	Completed
Provide implementation details and snapshots	Completed in assignment document

Security Measures Implemented

Security Measure	Implementation
Image vulnerability scanning	Trivy
Secrets management	Kubernetes Secret
Network restriction	Kubernetes NetworkPolicy
Least privilege execution	runAsNonRoot, runAsUser
Privilege escalation prevention	allowPrivilegeEscalation: false
Capability reduction	capabilities.drop: ALL
Resource control	CPU and memory requests/limits
Image registry	Amazon ECR
Kubernetes orchestration	Amazon EKS
Helm packaging	Helm chart

Notes

* Replace <account-id> with the AWS account ID before running ECR commands.
* Do not commit real AWS credentials, kubeconfig files, access keys, private keys, or production secrets.
* The secret.yaml file uses demo values only and should not contain real credentials.

Conclusion

This assignment demonstrates a secured microservices deployment lifecycle. Two Flask-based microservices were containerized using Docker, scanned using Trivy, pushed to Amazon ECR, and deployed on Amazon EKS. Kubernetes security controls such as Secrets, NetworkPolicy, resource limits, and container securityContext were implemented. Helm was also used to package and deploy the Kubernetes manifests.
