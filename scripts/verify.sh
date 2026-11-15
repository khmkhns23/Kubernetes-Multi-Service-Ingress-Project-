#!/usr/bin/env bash
# ==========================================================
# Verification Script for Student ID: 68130239
# Run on k8s-control: bash scripts/verify.sh
# ==========================================================

NS="id-239"

echo "=========================================================="
echo " 1. KUBERNETES RESOURCES (GET)"
echo "=========================================================="
kubectl get all,ingress,pv,pvc,cm -n "$NS" -o wide

echo -e "\n=========================================================="
echo " 2. INGRESS DETAILS (DESCRIBE)"
echo "=========================================================="
kubectl describe ingress id-239-ingress -n "$NS"

echo -e "\n=========================================================="
echo " 3. ENDPOINTS CHECK"
echo "=========================================================="
kubectl get endpoints -n "$NS"

echo -e "\n=========================================================="
echo " 4. HTTP ROUTING TEST (via External LB 192.168.1.20)"
echo "=========================================================="
echo "--- Test www.id-239.com/about ---"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" -H "Host: www.id-239.com" http://192.168.1.20/about

echo "--- Test www.id-239.com/research ---"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" -H "Host: www.id-239.com" http://192.168.1.20/research

echo "--- Test www.id-239.com/api/Hello_68130239 ---"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" -H "Host: www.id-239.com" http://192.168.1.20/api/Hello_68130239

echo "--- Test admin.id-239.com ---"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" -H "Host: admin.id-239.com" http://192.168.1.20/
