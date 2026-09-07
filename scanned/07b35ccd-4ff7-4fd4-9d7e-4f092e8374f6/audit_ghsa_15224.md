# [M] Grafana XSS via adding a link in General feature

## Summary
Severity: Medium
Advisory: GHSA-6wh2-8hw7-jw94
CVE: CVE-2018-18625
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-30
Source: https://github.com/advisories/GHSA-6wh2-8hw7-jw94
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <6.0.0-beta1

## Details
Grafana 5.3.1 has XSS via a link on the "Dashboard > All Panels > General" screen. NOTE: this issue exists because of an incomplete fix for CVE-2018-12099.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18625
- https://github.com/grafana/grafana/pull/11813
- https://github.com/grafana/grafana/pull/14984
- https://security.netapp.com/advisory/ntap-20200608-0008
