# [C] fabedge has insecure permissions

## Summary
Severity: Critical
Advisory: GHSA-c9cm-5j82-m6pj
CVE: CVE-2024-36536
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-07-24
Source: https://github.com/advisories/GHSA-c9cm-5j82-m6pj
Type: github-advisory

## Affected
- Go: `github.com/fabedge/fabedge` — affected >=0

## Details
Insecure permissions in fabedge v0.8.1 allows attackers to access sensitive data and escalate privileges by obtaining the service account's token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36536
- https://gist.github.com/HouqiyuA/381f100f2ba82a8ada03994aac5bb2e8
- https://github.com/fabedge/fabedge
- https://pkg.go.dev/vuln/GO-2024-3027
