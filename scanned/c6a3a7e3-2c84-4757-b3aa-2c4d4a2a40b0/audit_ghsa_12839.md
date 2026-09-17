# [H] Paranoidhttp Server-Side Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-v9mp-j8g7-2q6m
CVE: CVE-2023-24623
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-01-30
Source: https://github.com/advisories/GHSA-v9mp-j8g7-2q6m
Type: github-advisory

## Affected
- Go: `github.com/hakobe/paranoidhttp` — affected >=0 <0.3.0

## Details
Paranoidhttp before 0.3.0 allows SSRF because [::] is equivalent to the 127.0.0.1 address, but does not match the filter for private addresses.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24623
- https://github.com/hakobe/paranoidhttp/commit/07f671da14ce63a80f4e52432b32e8d178d75fd3
- https://github.com/hakobe/paranoidhttp
- https://github.com/hakobe/paranoidhttp/blob/master/CHANGELOG.md#v030-2023-01-19
- https://github.com/hakobe/paranoidhttp/compare/v0.2.0...v0.3.0
- https://pkg.go.dev/vuln/GO-2023-1526
