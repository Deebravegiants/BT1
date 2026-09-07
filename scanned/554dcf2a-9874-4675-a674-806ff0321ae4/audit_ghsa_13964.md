# [M] Cross Site Scripting in usememos/memos

## Summary
Severity: Medium
Advisory: GHSA-9w8x-5hv5-r6gw
CVE: CVE-2022-25978
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-15
Source: https://github.com/advisories/GHSA-9w8x-5hv5-r6gw
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.10.4-0.20230211093429-b11d2130a084

## Details
All versions of the package github.com/usememos/memos/server prior to 0.11.0 are vulnerable to Cross-site Scripting (XSS) due to insufficient checks on external resources, which allows malicious actors to introduce links starting with a javascript: scheme.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25978
- https://github.com/usememos/memos/issues/1026
- https://github.com/usememos/memos/commit/b11d2130a084385eb65c3761a3c841ebe9f81ae8
- https://pkg.go.dev/vuln/GO-2023-1566
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMUSEMEMOSMEMOSSERVER-3319070
- github.com/usememos/memos
