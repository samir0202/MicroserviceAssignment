# employee-service Docker image
docker build -t employee-service:latest -f ./employee-service/Dockerfile ./employee-service

# project-allocation-service Docker image
docker build -t project-allocation-service:latest -f ./project-allocation-service/Dockerfile ./project-allocation-service

docker tag employee-service:latest murshed23/employee-service:latest
docker tag project-allocation-service:latest murshed23/project-allocation-service:latest

# Pushing images to Docker Hub
docker push murshed23/employee-service:latest
docker push murshed23/project-allocation-service:latest

# Deploy services
kubectl apply -f kubernetes/mongo-deployment.yaml
kubectl apply -f kubernetes/employee-deployment.yaml
kubectl apply -f kubernetes/project-allocation-deployment.yaml