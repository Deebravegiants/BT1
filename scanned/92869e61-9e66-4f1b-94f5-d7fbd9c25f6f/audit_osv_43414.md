# [C] OpenChoreo: Unauthenticated access to data-plane operations via OpenChoreo cluster-gateway management APIs

## Summary
Severity: Critical
Advisory: CVE-2026-73843
Aliases: GHSA-qh9r-j7rp-4x2m, GO-2026-6362
CVSS: 9.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73843
Type: osv

## Details
OpenChoreo is a complete, open-source developer platform for Kubernetes. Prior to 1.0.2 and 1.1.2, internal/cluster-gateway/server.go served caller-facing management APIs on the externally reachable agent listener without authentication, allowing network-reachable attackers to invoke /api/proxy/ and /api/exec/ operations, proxy the data-plane Kubernetes API, and execute commands in workload pods in multi-cluster deployments. This issue is fixed in versions 1.0.2 and 1.1.2.

## References
- https://github.com/openchoreo/openchoreo/releases/tag/v1.0.2
- https://github.com/openchoreo/openchoreo/releases/tag/v1.1.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73843.json
- https://github.com/openchoreo/openchoreo/security/advisories/GHSA-qh9r-j7rp-4x2m
- https://nvd.nist.gov/vuln/detail/CVE-2026-73843
- https://github.com/openchoreo/openchoreo/commit/047d80ddc63b4b4b9dd67044d5cffcdbd77685ce
- https://github.com/openchoreo/openchoreo/commit/0aa0ffe1623bd8eb4235cb2a5854336695953c3a
- https://github.com/openchoreo/openchoreo/commit/b42eeb0f5dce95195a9781d7c5a1fe9e38f5da8f
- https://github.com/openchoreo/openchoreo/pull/4122
