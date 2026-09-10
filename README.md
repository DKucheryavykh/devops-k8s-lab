# DevOps Kubernetes Lab

Практический DevOps-проект, демонстрирующий полный цикл контейнеризации, оркестрации, мониторинга и CI/CD для небольшого веб-приложения.

## Architecture

```text
Developer
    |
    v
  GitHub
    |
    v
GitHub Actions
    |
    +--> Python validation
    +--> Docker Compose validation
    +--> Helm lint / template
    +--> Docker Buildx
              |
              v
             GHCR
              |
              v
             Helm
              |
              v
        Kubernetes (kind)
              |
              v
         ingress-nginx
              |
              v
        Kubernetes Service
              |
              v
      Flask / Gunicorn Pods
              |
              v
          /metrics
              |
              v
        ServiceMonitor
              |
              v
          Prometheus
```

## Technology Stack

- Python 3.12
- Flask
- Gunicorn
- Docker
- Docker Compose
- Nginx
- HAProxy
- Kubernetes
- kind
- ingress-nginx
- Helm
- Prometheus Operator
- ServiceMonitor
- GitHub Actions
- GitHub Container Registry (GHCR)

## Application

Приложение предоставляет несколько HTTP endpoints:

- `/` — информация о приложении и окружении
- `/health` — liveness endpoint
- `/ready` — readiness endpoint
- `/metrics` — метрики в формате Prometheus

Пример ответа:

```json
{
  "environment": "kubernetes",
  "message": "Running from Helm",
  "service": "devops-k8s-lab"
}
```

## Docker

Сборка Docker-образа:

```bash
docker build -t devops-k8s-lab .
```

Запуск контейнера:

```bash
docker run --rm -p 8080:8080 devops-k8s-lab
```

Приложение запускается через Gunicorn от непривилегированного пользователя.

Docker-образ содержит `HEALTHCHECK`, использующий endpoint `/health`.

## Docker Compose

Docker Compose используется для демонстрации работы приложения через Nginx и HAProxy.

```text
              +--> Nginx  :8088 --+
Client -------|                    +--> Flask / Gunicorn :8080
              +--> HAProxy :8090 --+
```

Запуск:

```bash
docker compose up -d --build
```

Проверка через Nginx:

```bash
curl http://127.0.0.1:8088/
```

Проверка через HAProxy:

```bash
curl http://127.0.0.1:8090/
```

HAProxy Stats:

```text
http://127.0.0.1:8404/stats
```

## Kubernetes

Для локального Kubernetes-кластера используется `kind`.

Архитектура кластера:

```text
devops-lab-control-plane
devops-lab-worker
devops-lab-worker2
```

Создание кластера:

```bash
kind create cluster \
  --name devops-lab \
  --config kind-config.yaml
```

Проверка:

```bash
kubectl get nodes
```

Приложение использует:

- Deployment с несколькими репликами
- ClusterIP Service
- ConfigMap
- Ingress
- readinessProbe
- livenessProbe
- CPU/memory requests и limits

## Helm

Основной способ развёртывания приложения — Helm chart:

```text
helm/devops-demo
```

Установка:

```bash
helm install devops-demo helm/devops-demo \
  --namespace devops-helm \
  --create-namespace \
  --set ingress.host=helm.devops-lab.local
```

Обновление:

```bash
helm upgrade devops-demo helm/devops-demo \
  --namespace devops-helm \
  --set ingress.host=helm.devops-lab.local
```

Проверка rollout:

```bash
kubectl rollout status deployment/devops-demo -n devops-helm
```

Изменение ConfigMap вызывает rolling update Deployment через checksum annotation.

## Container Registry

GitHub Actions собирает Docker-образ и публикует его в GitHub Container Registry:

```text
ghcr.io/dkucheryavykh/devops-k8s-lab
```

Создаются два варианта тега:

```text
latest
<git-commit-sha>
```

Helm использует образ непосредственно из GHCR:

```yaml
image:
  repository: ghcr.io/dkucheryavykh/devops-k8s-lab
  tag: latest
  pullPolicy: Always
```

## Ingress

Для маршрутизации HTTP-трафика используется ingress-nginx.

Путь запроса:

```text
Client
  |
  v
kind :8080
  |
  v
ingress-nginx
  |
  v
Ingress
  |
  v
ClusterIP Service
  |
  v
Application Pods
```

Проверка:

```bash
curl -H "Host: helm.devops-lab.local" \
  http://127.0.0.1:8080/
```

## Monitoring

Мониторинг построен на Prometheus Operator.

```text
Prometheus
    |
    v
ServiceMonitor
    |
    v
Kubernetes Service
    |
    +--> Pod 1 /metrics
    +--> Pod 2 /metrics
    +--> Pod 3 /metrics
```

ServiceMonitor обнаруживает приложение по Kubernetes labels.

Приложение экспортирует метрики:

```text
app_requests_total
app_uptime_seconds
```

Prometheus собирает метрики отдельно с каждой реплики приложения.

## CI/CD

Pipeline реализован с помощью GitHub Actions:

```text
Push / Pull Request
        |
        v
     Checkout
        |
        v
Python syntax validation
        |
        v
Docker Compose validation
        |
        v
     Helm lint
        |
        v
   Helm template
        |
        v
  Docker Buildx
        |
        v
   Build image
        |
        v
   Push to GHCR
```

При `push` в `main` Docker-образ автоматически собирается и публикуется в GHCR.

Для авторизации используется встроенный `GITHUB_TOKEN`, поэтому отдельный registry password в репозитории не хранится.

## Repository Structure

```text
devops-k8s-lab/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── app.py
│   └── requirements.txt
├── haproxy/
│   └── haproxy.cfg
├── helm/
│   └── devops-demo/
├── kubernetes/
├── monitoring/
│   └── servicemonitor.yaml
├── nginx/
│   └── nginx.conf
├── Dockerfile
├── docker-compose.yml
├── kind-config.yaml
└── README.md
```

## What This Project Demonstrates

Проект демонстрирует практическую работу с Docker, reverse proxy, Kubernetes, Helm, Ingress, health/readiness probes, rolling updates, Prometheus monitoring, GitHub Actions и GitHub Container Registry.

Проект создан как практическая DevOps-лаборатория и portfolio project.