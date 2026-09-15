# [M] Grafana Arbitrary File Read

## Summary
Severity: Medium
Advisory: GHSA-4pwp-cx67-5cpx
CVE: CVE-2019-19499
CWE: CWE-200, CWE-22, CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N/E:P (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-4pwp-cx67-5cpx
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <6.4.4

## Details
Grafana <= 6.4.3 has an Arbitrary File Read vulnerability, which could be exploited by an authenticated attacker that has privileges to modify the data source configurations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19499
- https://github.com/grafana/grafana/pull/20192
- https://github.com/grafana/grafana/commit/19dbd27c5caa1a160bd5854b65a4e1fe2a8a4f00
- https://github.com/grafana/grafana
- https://github.com/grafana/grafana/blob/master/CHANGELOG.md#644-2019-11-06
- https://security.netapp.com/advisory/ntap-20200918-0003
