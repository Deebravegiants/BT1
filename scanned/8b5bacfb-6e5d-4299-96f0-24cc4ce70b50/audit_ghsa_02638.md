# [M] Path traversal in Grafana Loki

## Summary
Severity: Medium
Advisory: GHSA-grj5-8x6q-hc9q
CVE: CVE-2021-36156
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-grj5-8x6q-hc9q
Type: github-advisory

## Affected
- Go: `github.com/grafana/loki` — affected >=0 <2.3.0

## Details
An issue was discovered in Grafana Loki through 2.2.1. The header value X-Scope-OrgID is used to construct file paths for rules files, and if crafted to conduct directory traversal such as ae ../../sensitive/path/in/deployment pathname, then Loki will attempt to parse a rules file at that location and include some of the contents in the error message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36156
- https://github.com/grafana/loki/pull/4020
- https://github.com/grafana/loki/pull/4020#issue-694377133
- https://github.com/grafana/loki
- https://github.com/grafana/loki/releases/tag/v2.3.0
