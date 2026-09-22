# [H] Fleet's unbounded request body read allows remote Denial of Service

## Summary
Severity: High
Advisory: GHSA-99hj-44vg-hfcp
CVE: CVE-2026-26061
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-99hj-44vg-hfcp
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.43.5-0.20260113202849-bbc1aef2987d

## Details
### Summary

Fleet contained multiple unauthenticated HTTP endpoints that read request bodies without enforcing a size limit. An unauthenticated attacker could exploit this behavior by sending large or repeated HTTP payloads, causing excessive memory allocation and resulting in a denial-of-service (DoS) condition.

### Impact

An unauthenticated attacker could cause the Fleet server process to exhaust available memory and restart by sending oversized or repeated HTTP requests to affected endpoints.

This vulnerability impacts **availability only**. There is:

- No exposure of sensitive data
- No authentication bypass
- No privilege escalation
- No integrity impact

### Workarounds

If upgrading immediately is not possible, the following mitigations can reduce exposure:

- Apply request body size limits at a reverse proxy or load balancer (e.g., NGINX, Envoy).
- Restrict network access to endpoints to known IP ranges where feasible.
- Monitor memory usage and restart frequency for abnormal patterns.

### For More Information

If there are any questions or concerns about this advisory, please contact us at:

Email Fleet at [security@fleetdm.com](mailto:security@fleetdm.com)

### Credits

Fleet thanks @fuzzztf for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-99hj-44vg-hfcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-26061
- https://github.com/fleetdm/fleet
