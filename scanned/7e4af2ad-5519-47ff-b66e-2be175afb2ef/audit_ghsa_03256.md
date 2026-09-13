# [H] Path traversal in u-root

## Summary
Severity: High
Advisory: GHSA-58pf-pcwv-qg85
CVE: CVE-2020-7665
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-58pf-pcwv-qg85
Type: github-advisory

## Affected
- Go: `github.com/u-root/u-root` — affected >=0 <0.9.0

## Details
This affects all versions of package github.com/u-root/u-root/pkg/uzip. It is vulnerable to both leading and non-leading relative path traversal attacks in zip file extraction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7665
- https://github.com/u-root/u-root/pull/1817
- https://github.com/u-root/u-root/pull/2344
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMUROOTUROOTPKGUZIP-570441
