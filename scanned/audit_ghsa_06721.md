# [M] Skipper: Unbounded Request Body Read in Admission Webhook Causes Memory Exhaustion DoS

## Summary
Severity: Medium
Advisory: GHSA-cwxq-rc9x-2jvv
CVE: CVE-2026-54247
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-cwxq-rc9x-2jvv
Type: github-advisory

## Affected
- Go: `github.com/zalando/skipper` — affected >=0 <0.26.22

## Details
## Summary

The Kubernetes admission webhook handler reads the entire request body using `io.ReadAll(r.Body)` without any size limit. Any client that can reach the webhook port within the cluster can send a multi-GB payload, causing the skipper process to exhaust memory and be OOM-killed. This disrupts all Kubernetes admission control, potentially blocking all pod creation and updates.

## Vulnerable Code

```go
// dataclients/kubernetes/admission/admission.go:76
body, err := io.ReadAll(r.Body)  // <-- NO SIZE LIMIT
if err != nil {
    log.Errorf("Failed to read request: %v", err)
    w.WriteHeader(http.StatusInternalServerError)
    invalidRequests.WithLabelValues(admitterName).Inc()
    return
}

var review admissionReview
err = json.Unmarshal(body, &review)
```

For comparison, the OPA filter has a body size limit:

```go
// filters/openpolicyagent/openpolicyagent.go:68-70
const DefaultMaxRequestBodySize = 1 << 20 // 1MB

// OPA uses a bufferedBodyReader with size limits
```

## Attack Path

1. Attacker identifies the admission webhook endpoint (default: `:9443/admission` or configured path)
2. Attacker sends: `POST /admission HTTP/1.1, Content-Type: application/json` with a multi-GB request body
3. `io.ReadAll(r.Body)` allocates unbounded memory for the entire body
4. Skipper process is OOM-killed by the Kubernetes kubelet

## Permission Boundary Analysis

- **Attacker**: Any client with network access to the admission webhook port within the Kubernetes cluster
- **Boundary crossed**: Memory safety — unbounded allocation from attacker-controlled input
- **Preconditions**: Admission webhook endpoint must be network-reachable (default Kubernetes deployment exposes it within cluster network)
- **Comparison**: OPA filter has `DefaultMaxRequestBodySize` (1MB) and semaphore-based memory limit; admission handler has neither

## Evidence

| File | Lines | Description |
|------|-------|-------------|
| `dataclients/kubernetes/admission/admission.go` | 76 | `io.ReadAll(r.Body)` without size limit |
| `filters/openpolicyagent/openpolicyagent.go` | 68-70 | OPA filter has `DefaultMaxRequestBodySize` = 1MB |
| `filters/openpolicyagent/openpolicyagent.go` | 1333-1336 | OPA uses `bufferedBodyReader` with size limits |

## Tests

- `dataclients/kubernetes/admission/admission_test.go` exists but **does not test body size limits**

## Impact

The admission webhook handler reads the entire request body using io.ReadAll(r.Body) without a size limit. An attacker with in-cluster network access and a valid Kubernetes client certificate can send a multi-GB payload to the webhook endpoint, causing the skipper process to exhaust memory and be OOM-killed. This disrupts admission control for Ingress and RouteGroup resources until the process is automatically restarted by the kubelet.

Scope of impact: Ingress and RouteGroup admission only — not pod creation or other admission controllers.

Recovery: Kubernetes automatically restarts the OOM-killed process, limiting downtime.

Prerequisites: (1) In-cluster network access to the webhook port, (2) valid Kubernetes client certificate.

## Mitigation

1. Add `http.MaxBytesReader` or equivalent body size limit before `io.ReadAll`
2. Follow the OPA filter pattern: define `DefaultMaxRequestBodySize` and use a buffered reader with size limits
3. Add a configurable `--admission-max-body-size` flag

## References
- https://github.com/zalando/skipper/security/advisories/GHSA-cwxq-rc9x-2jvv
- https://github.com/zalando/skipper
- https://github.com/zalando/skipper/releases/tag/v0.26.22
