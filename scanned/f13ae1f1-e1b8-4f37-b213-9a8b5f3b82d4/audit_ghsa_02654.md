# [M] Path traversal in Grafana Cortex

## Summary
Severity: Medium
Advisory: GHSA-jphm-g89m-v42p
CVE: CVE-2021-36157
CWE: CWE-22
Ecosystem: Go
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-jphm-g89m-v42p
Type: github-advisory

## Affected
- Go: `github.com/cortexproject/cortex` — affected >=0

## Details
An issue was discovered in Grafana Cortex through 1.9.0. The header value X-Scope-OrgID is used to construct file paths for rules files, and if crafted to conduct directory traversal such as ae ../../sensitive/path/in/deployment pathname, then Cortex will attempt to parse a rules file at that location and include some of the contents in the error message. (Other Cortex API requests can also be sent a malicious OrgID header, e.g., tricking the ingester into writing metrics to a different location, but the effect is nuisance rather than information disclosure.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36157
- https://github.com/cortexproject/cortex/pull/4375
- https://github.com/cortexproject/cortex/commit/d9e1f81f40c607b9e97c2fc6db70ae54679917c4
- https://github.com/cortexproject/cortex
- https://grafana.com/docs/grafana/latest/release-notes
