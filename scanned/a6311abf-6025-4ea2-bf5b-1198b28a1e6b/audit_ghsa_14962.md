# [M] go-retryablehttp can leak basic auth credentials to log files

## Summary
Severity: Medium
Advisory: GHSA-v6v8-xj6m-xwqh
CVE: CVE-2024-6104
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-24
Source: https://github.com/advisories/GHSA-v6v8-xj6m-xwqh
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/go-retryablehttp` — affected >=0 <0.7.7

## Details
go-retryablehttp prior to 0.7.7 did not sanitize urls when writing them to its log file. This could lead to go-retryablehttp writing sensitive HTTP basic auth credentials to its log file. This vulnerability, CVE-2024-6104, was fixed in go-retryablehttp 0.7.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6104
- https://github.com/hashicorp/go-retryablehttp/commit/a99f07beb3c5faaa0a283617e6eb6bcf25f5049a
- https://discuss.hashicorp.com/c/security
- https://discuss.hashicorp.com/t/hcsec-2024-12-go-retryablehttp-can-leak-basic-auth-credentials-to-log-files/68027
- https://github.com/advisories/GHSA-v6v8-xj6m-xwqh
- https://github.com/hashicorp/go-retryablehttp
