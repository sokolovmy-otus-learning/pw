#!/bin/bash


# Переменные
NAMESPACE="monitoring"
HELM_RELEASE="kube-prom-stack"
VALUES_FILE="prometheus-values.yaml"

# Проверка наличия prometheus-values.yaml
if [ ! -f "$VALUES_FILE" ]; then
    echo "Ошибка: Файл $VALUES_FILE не найден."
    exit 1
fi

# Проверка существования PVC
if ! kubectl get pvc grafana-dashboards-pvc -n $NAMESPACE &> /dev/null; then
    echo "Ошибка: PVC grafana-dashboards-pvc не найден в неймспейсе $NAMESPACE."
    exit 1
fi

# Создание неймспейса, если не существует
echo "Создаём неймспейс $NAMESPACE, если не существует..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Добавление репозитория Helm
echo "Добавляем репозиторий prometheus-community..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Установка kube-prometheus-stack
echo "Устанавливаем kube-prometheus-stack..."
helm upgrade --install $HELM_RELEASE prometheus-community/kube-prometheus-stack \
  -f $VALUES_FILE \
  --namespace $NAMESPACE \
  --wait

# Проверка статуса
echo "Проверяем статус пода Grafana..."
kubectl get pods -n $NAMESPACE | grep grafana

echo "Проверяем статус пода Prometheus..."
kubectl get pods -n $NAMESPACE | grep prometheus

echo "Установка завершена!"
echo "Доступ к Grafana: kubectl port-forward svc/$HELM_RELEASE-grafana -n $NAMESPACE 3000:80"
echo "Логин: admin, Пароль: prom-operator (или другой, указанный в $VALUES_FILE)"
echo "Доступ к Prometheus: kubectl port-forward svc/$HELM_RELEASE-prometheus -n $NAMESPACE 9090:9090"