# [H] Path traversal in ginadmin

## Summary
Severity: High
Advisory: GHSA-9pg5-3pjc-f8wm
CVE: CVE-2022-30427
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-26
Source: https://github.com/advisories/GHSA-9pg5-3pjc-f8wm
Type: github-advisory

## Affected
- Go: `github.com/gphper/ginadmin` — affected >=0

## Details
In ginadmin through 05-10-2022 the incoming path value is not filtered, resulting in directory traversal. A [patch](https://github.com/gphper/ginadmin/commit/726109f01ad23523715f36f7d272958064666a30) is available on the `master` branch of the repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30427
- https://github.com/gphper/ginadmin/issues/8
- https://github.com/gphper/ginadmin/commit/726109f01ad23523715f36f7d272958064666a30
- github.com/gphper/ginadmin
