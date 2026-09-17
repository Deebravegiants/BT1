# [H] Lancet vulnerable to path traversal when unzipping files

## Summary
Severity: High
Advisory: GHSA-pp3f-xrw5-q5j4
CVE: CVE-2022-41920
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-pp3f-xrw5-q5j4
Type: github-advisory

## Affected
- Go: `github.com/duke-git/lancet/v2` — affected >=2.0.0 <2.1.10
- Go: `github.com/duke-git/lancet` — affected >=0 <1.3.4

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

ZipSlip issue when use fileutil package to unzip files.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

It will fixed in v2.1.10, Please upgrade version to v2.1.10 or above.
Users who use v1.x.x should upgrade v1.3.4 or above.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

No, users have to upgrade version.

## References
- https://github.com/duke-git/lancet/security/advisories/GHSA-pp3f-xrw5-q5j4
- https://nvd.nist.gov/vuln/detail/CVE-2022-41920
- https://github.com/duke-git/lancet/issues/62
- https://github.com/duke-git/lancet/commit/f133b32faa05eb93e66175d01827afa4b7094572
- https://github.com/duke-git/lancet/commit/f869a0a67098e92d24ddd913e188b32404fa72c9
- https://github.com/duke-git/lancet
- https://pkg.go.dev/vuln/GO-2022-1114
