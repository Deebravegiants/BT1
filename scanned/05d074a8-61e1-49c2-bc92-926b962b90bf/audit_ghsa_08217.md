# [M] Grafana: Users can generate Service Account tokens after permissions removal

## Summary
Severity: Medium
Advisory: GHSA-wfhv-mj62-f5xh
CVE: CVE-2026-33381
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-wfhv-mj62-f5xh
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <1.9.2-0.20260513165311-fb7336fc36c1

## Details
When a user's access to mint tokens for a service account is revoked, it is sometimes still possible to do so for a few seconds after the event. The user will eventually lose access to do this.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33381
- https://github.com/grafana/grafana/commit/fb7336fc36c14e1ff869482c5085ddb9f39e1b86
- https://github.com/grafana/grafana
- https://grafana.com/security/security-advisories/cve-2026-33381
