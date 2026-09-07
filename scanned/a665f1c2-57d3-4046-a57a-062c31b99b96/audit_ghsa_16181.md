# [M] Stored XSS using two files in usememos/memos

## Summary
Severity: Medium
Advisory: GHSA-5r2g-59px-3q9w
CVE: CVE-2023-0109
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-11-15
Source: https://github.com/advisories/GHSA-5r2g-59px-3q9w
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.10.0

## Details
A stored cross-site scripting (XSS) vulnerability was discovered in usememos/memos version 0.9.1. This vulnerability allows an attacker to upload a JavaScript file containing a malicious script and reference it in an HTML file. When the HTML file is accessed, the malicious script is executed. This can lead to the theft of sensitive information, such as login credentials, from users visiting the affected website. The issue has been fixed in version 0.10.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0109
- https://github.com/usememos/memos/commit/46c13a4b7f675b92d297df6dabb4441f13c7cd9c
- https://github.com/usememos/memos
- https://huntr.com/bounties/1899ffb2-ce1e-4dc0-af96-972612190f6e
- https://pkg.go.dev/vuln/GO-2024-3274
