# [H] Prometheus: Remote read endpoint allows denial of service via crafted snappy payload

## Summary
Severity: High
Advisory: GHSA-8rm2-7qqf-34qm
CVE: CVE-2026-42154
CWE: CWE-400, CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-8rm2-7qqf-34qm
Type: github-advisory

## Affected
- Go: `github.com/prometheus/prometheus` — affected >=0.306.0 <0.311.3
- Go: `github.com/prometheus/prometheus` — affected >=0 <0.305.2
- Go: `github.com/prometheus/prometheus` — affected >=1.0.0-rc.0

## Details
### Impact

The remote read endpoint (`/api/v1/read`) does not validate the declared decoded length in a snappy-compressed request body before allocating memory.
An unauthenticated attacker can send a small payload that causes a huge heap allocation per request. Under concurrent load this can exhaust available memory and crash the Prometheus process.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Fixed in 3.11.3 and 3.5.3 LTS. Users should upgrade to these versions or later.

### Workarounds
User who can not upgrade can place Prometheus behind a reverse proxy or firewall that requires authentication before requests reach /api/v1/read.

## References
- https://github.com/prometheus/prometheus/security/advisories/GHSA-8rm2-7qqf-34qm
- https://nvd.nist.gov/vuln/detail/CVE-2026-42154
- https://github.com/prometheus/prometheus/pull/18584
- https://github.com/prometheus/prometheus/pull/18585
- https://github.com/prometheus/prometheus
- https://github.com/prometheus/prometheus/releases/tag/v3.11.3
- https://github.com/prometheus/prometheus/releases/tag/v3.5.3
