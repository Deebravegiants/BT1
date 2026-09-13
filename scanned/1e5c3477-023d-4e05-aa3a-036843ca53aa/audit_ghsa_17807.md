# [M] Grafana Alerting VictorOps integration could be exposed to users with Viewer permission

## Summary
Severity: Medium
Advisory: GHSA-wxcc-2f3q-4h58
CVE: CVE-2024-11741
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-01-31
Source: https://github.com/advisories/GHSA-wxcc-2f3q-4h58
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=11.4.0 <11.4.1
- Go: `github.com/grafana/grafana` — affected >=11.3.0 <11.3.3
- Go: `github.com/grafana/grafana` — affected >=11.2.0 <11.2.6
- Go: `github.com/grafana/grafana` — affected >=11.1.0 <11.1.11
- Go: `github.com/grafana/grafana` — affected >=11.0.0 <11.0.11
- Go: `github.com/grafana/grafana` — affected >=1.9.2 <10.4.15
- Go: `github.com/grafana/grafana` — affected >=0 <0.0.0-20250129224826-70073427041e
- Go: `github.com/grafana/grafana` — affected >=0.0.0 <1.9.2-0.20250129224826-70073427041e

## Details
Grafana is an open-source platform for monitoring and observability. 
The Grafana Alerting VictorOps integration was not properly protected and could be exposed to users with Viewer permission. 
Fixed in versions 11.5.0, 11.4.1, 11.3.3, 11.2.6, 11.1.11, 11.0.11 and 10.4.15

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11741
- https://github.com/grafana/grafana/commit/70073427041e15c353e0d467b714527584765aea
- https://github.com/grafana/grafana
- https://grafana.com/security/security-advisories/cve-2024-11741
- https://pkg.go.dev/vuln/GO-2025-3438
- https://security.netapp.com/advisory/ntap-20250509-0006
