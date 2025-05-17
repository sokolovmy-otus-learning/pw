kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -



kubectl port-forward svc/prometheus -n monitoring 9090:9090


kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml