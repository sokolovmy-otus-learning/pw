helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts

helm repo update




helm upgrade --install loki grafana/loki-stack -n monitoring --create-namespace --set loki.isDefault=false

helm upgrade --install prom prometheus-community/kube-prometheus-stack \
  -n monitoring --set alertmanager.enabled=false --set grafana.sidecar.datasources.alertmanager=false


# helm upgrade --install grafana grafana/grafana -n monitoring --set sidecar.datasources.enabled=true \
#   --set sidecar.dashboards.enabled=true \
#   --set persistence.enabled=true \
#   --set persistence.size=1Gi
