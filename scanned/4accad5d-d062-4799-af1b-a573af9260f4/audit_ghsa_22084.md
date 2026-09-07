# [M] Grafana Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7phr-6cc9-4m5q
CVE: CVE-2019-13068
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7phr-6cc9-4m5q
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <6.2.5

## Details
`public/app/features/panel/panel_ctrl.ts` in Grafana before 6.2.5 allows HTML Injection in panel drilldown links (via the Title or url field).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13068
- https://github.com/grafana/grafana/issues/17718
- https://github.com/grafana/grafana
- https://github.com/grafana/grafana/releases/tag/v6.2.5
- https://security.netapp.com/advisory/ntap-20190710-0001
- http://packetstormsecurity.com/files/171500/Grafana-6.2.4-HTML-Injection.html
