# [H] Arbitrary file read in ginadmin

## Summary
Severity: High
Advisory: GHSA-5824-6jfv-xr3r
CVE: CVE-2022-30428
CWE: CWE-22, CWE-552
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-26
Source: https://github.com/advisories/GHSA-5824-6jfv-xr3r
Type: github-advisory

## Affected
- Go: `github.com/gphper/ginadmin` — affected >=0

## Details
In ginadmin through 05-10-2022, the incoming path value is not filtered, resulting in arbitrary file reading. A [patch](https://github.com/gphper/ginadmin/commit/726109f01ad23523715f36f7d272958064666a30) is available on the `master` branch of the repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30428
- https://github.com/gphper/ginadmin/issues/9
- https://github.com/gphper/ginadmin/commit/726109f01ad23523715f36f7d272958064666a30
- github.com/gphper/ginadmin
