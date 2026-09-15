# [M] Envoy Gateway: Wasm cache ServeHTTP reads mappingPath2Cache without lock

## Summary
Severity: Medium
Advisory: GHSA-8fv2-88gg-hm7q
CVE: CVE-2026-53715
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-8fv2-88gg-hm7q
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/gateway` — affected >=1.8.0-rc.0 <1.8.1
- Go: `github.com/envoyproxy/gateway` — affected >=0 <1.7.4

## Details
Vulnerability report without repro case. Repro case may be added later after harness is complete.

**Preconditions (4):**
- Pod-network reachability to :18002 (no auth)
- Tenant can create EnvoyExtensionPolicy (baseline)
- Attacker pod floods GET while churning EnvoyExtensionPolicy with distinct Wasm URLs
- Read at :153 must overlap a write at :201/:209 (probabilistic, attacker controls both rates)

**Description:**

httpserver.go:153 reads s.mappingPath2Cache with no lock while httpserver.go:201/209 write it under s.Lock(); the struct uses a plain map. Writer is tenant-reachable via EnvoyExtensionPolicy translation, reader is pod-network-reachable on :18002 with per-request goroutines. Go's concurrent map read+write detection calls runtime.throw, which net/http's per-conn recover cannot catch, so the controller process exits — cross-tenant control-plane DoS. Capped at MEDIUM: DoS-only, k8s restarts pod, timing-dependent trigger.

## References
- https://github.com/envoyproxy/gateway/security/advisories/GHSA-8fv2-88gg-hm7q
- https://github.com/envoyproxy/gateway
