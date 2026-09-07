# [M] Zinc Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4fgv-8448-gf82
CVE: CVE-2022-32171
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-4fgv-8448-gf82
Type: github-advisory

## Affected
- Go: `github.com/zincsearch/zincsearch` — affected >=0.1.9 <0.3.2
- Go: `github.com/zinclabs/zinc` — affected >=0.1.9 <0.3.2

## Details
In Zinc, versions v0.1.9 through v0.3.1 are vulnerable to Stored Cross-Site Scripting when using the delete user functionality. When an authenticated user deletes a user having a XSS payload in the user id field, the javascript payload will be executed and allow an attacker to access the user’s credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32171
- https://github.com/zinclabs/zinc/commit/3376c248bade163430f9347742428f0a82cd322d
- https://github.com/zincsearch/zincsearch/commit/3376c248bade163430f9347742428f0a82cd322d
- https://www.mend.io/vulnerability-database/CVE-2022-32171
