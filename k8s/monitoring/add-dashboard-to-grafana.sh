#!/bin/bash

# Проверка наличия kubectl
if ! command -v kubectl &> /dev/null; then
    echo "kubectl не установлен. Пожалуйста, установите kubectl."
    exit 1
fi

# Переменные
NAMESPACE="monitoring"
HELM_RELEASE="kube-prom-stack"
DASHBOARD_FILE="$1"

# Проверка аргумента
if [ -z "$DASHBOARD_FILE" ]; then
    echo "Ошибка: Укажите путь к JSON-файлу дашборда."
    echo "Пример: $0 ./k8s-pod-uptime.json"
    exit 1
fi

if [ ! -f "$DASHBOARD_FILE" ]; then
    echo "Ошибка: Файл $DASHBOARD_FILE не существует."
    exit 1
fi

# Получение имени файла
DASHBOARD_FILENAME=$(basename "$DASHBOARD_FILE")

# Поиск пода Grafana
echo "Ищем под Grafana в неймспейсе $NAMESPACE..."
GRAFANA_POD=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=grafana -o jsonpath="{.items[0].metadata.name}")

if [ -z "$GRAFANA_POD" ]; then
    echo "Ошибка: Под Grafana не найден в неймспейсе $NAMESPACE."
    exit 1
fi

echo "Найден под Grafana: $GRAFANA_POD"

# Копирование файла в PVC
echo "Копирую $DASHBOARD_FILE в /tmp/dashboards/$DASHBOARD_FILENAME..."
kubectl cp "$DASHBOARD_FILE" $NAMESPACE/$GRAFANA_POD:/tmp/dashboards/$DASHBOARD_FILENAME -n $NAMESPACE

# Проверка наличия файла
echo "Проверяю наличие файла в поде..."
kubectl exec -n $NAMESPACE $GRAFANA_POD -- ls /tmp/dashboards | grep "$DASHBOARD_FILENAME"

if [ $? -eq 0 ]; then
    echo "Файл $DASHBOARD_FILENAME успешно добавлен!"
    echo "Проверьте дашборд в Grafana: kubectl port-forward svc/$HELM_RELEASE-grafana -n $NAMESPACE 3000:80"
else
    echo "Ошибка: Файл не найден в /tmp/dashboards. Проверьте копирование."
    exit 1
fi