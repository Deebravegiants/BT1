# [M] Grafana XSS in Dashboard Text Panel

## Summary
Severity: Medium
Advisory: GHSA-cmq2-j8v8-2q44
CVE: CVE-2018-18623
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-30
Source: https://github.com/advisories/GHSA-cmq2-j8v8-2q44
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <6.0.0-beta1

## Details
Grafana 5.3.1 has XSS via the "Dashboard > Text Panel" screen. NOTE: this issue exists because of an incomplete fix for CVE-2018-12099.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18623
- https://github.com/grafana/grafana/issues/15293
- https://github.com/grafana/grafana/issues/4117
- https://github.com/grafana/grafana/pull/11813
- https://github.com/grafana/grafana/pull/14984
- https://github.com/grafana/grafana/releases/tag/v6.0.0
- https://security.netapp.com/advisory/ntap-20200608-0008
