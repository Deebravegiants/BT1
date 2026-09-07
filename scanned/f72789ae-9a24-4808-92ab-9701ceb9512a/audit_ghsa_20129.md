# [H] Casdoor arbitrary file deletion vulnerability via uploadFile function

## Summary
Severity: High
Advisory: GHSA-f93f-55c2-8c89
CVE: CVE-2022-44942
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-12-07
Source: https://github.com/advisories/GHSA-f93f-55c2-8c89
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0 <1.126.1

## Details
Casdoor before v1.126.1 was discovered to contain an arbitrary file deletion vulnerability via the `uploadFile` function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-44942
- https://github.com/casdoor/casdoor/issues/1171
- https://github.com/casdoor/casdoor/pull/1174
- https://github.com/casdoor/casdoor
- https://github.com/casdoor/casdoor/releases/tag/v1.126.1
