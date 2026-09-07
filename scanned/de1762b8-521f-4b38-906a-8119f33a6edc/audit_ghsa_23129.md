# [M] Grafana XSS via a column style

## Summary
Severity: Medium
Advisory: GHSA-9hv8-4frf-cprf
CVE: CVE-2018-18624
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9hv8-4frf-cprf
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <7.0.0

## Details
Grafana has a XSS vulnerability via a column style on the "Dashboard > Table Panel" screen. NOTE: this issue exists because of an incomplete fix for CVE-2018-12099.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18624
- https://github.com/grafana/grafana/pull/11813
- https://github.com/grafana/grafana/pull/23816
- https://github.com/grafana/grafana/commit/0284747c88eb9435899006d26ffaf65f89dec88e
- https://github.com/grafana/grafana
- https://security.netapp.com/advisory/ntap-20200608-0008
