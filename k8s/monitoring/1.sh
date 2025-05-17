helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/

helm repo update

# metric server

helm upgrade --install metrics-server metrics-server/metrics-server \
  --namespace kube-system \
  -f metrics-server-values.yaml





# helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f grafana-values.yaml


helm install kube-state-metrics prometheus-community/kube-state-metrics -n monitoring



# kubectl port-forward svc/kube-prometheus-stack-grafana 3000:80 -n monitoring
# Откройте http://localhost:3000 (по умолчанию логин: admin, пароль: prom-operator).




# loki


helm install loki grafana/loki-stack -n monitoring \
  --create-namespace \
  --set grafana.enabled=false \
  --set promtail.enabled=true \
  --set promtail.config.clients[0].url=http://loki.monitoring.svc:3100/loki/api/v1/push



kubectl apply -f loki-dashboards.yaml
