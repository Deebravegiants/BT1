# [M] Envoy Gateway: Nil-dereference when SecurityPolicy targets TCPRoute without spec.authorization

## Summary
Severity: Medium
Advisory: GHSA-m2v6-2jmh-4c68
CVE: CVE-2026-53719
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-m2v6-2jmh-4c68
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/gateway` — affected >=1.8.0-rc.0 <1.8.1
- Go: `github.com/envoyproxy/gateway` — affected >=0 <1.7.4

## Details
Vulnerability report without repro case. Repro case may be added later after harness is complete.

**Preconditions (4):**
- Tenant has SecurityPolicy + TCPRoute RBAC (baseline)
- Tenant namespace permitted to attach TCPRoute to a Gateway listener
- spec.authorization omitted (the trigger)
- No admission webhook blocks the shape

**Description:**

A namespace-scoped tenant can deterministically panic the gatewayapi runner on every reconcile with a single CRD; the recover() in message/watchutil.go:53 keeps the process alive but unwinds the entire handle() callback in runner/runner.go:192, so xDS/Infra IR publishing stalls controller-wide until an admin deletes the object. Data plane keeps serving last-good config.

## References
- https://github.com/envoyproxy/gateway/security/advisories/GHSA-m2v6-2jmh-4c68
- https://github.com/envoyproxy/gateway
