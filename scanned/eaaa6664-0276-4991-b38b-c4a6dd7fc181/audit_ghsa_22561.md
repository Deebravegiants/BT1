# [H] Arbitrary command execution in Minidoc

## Summary
Severity: High
Advisory: GHSA-f7ff-xf87-f22q
CVE: CVE-2022-29637
CWE: CWE-434
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-27
Source: https://github.com/advisories/GHSA-f7ff-xf87-f22q
Type: github-advisory

## Affected
- Go: `github.com/mindoc-org/mindoc` — affected >=0

## Details
An arbitrary file upload vulnerability in Mindoc v2.1-beta.5 allows attackers to execute arbitrary commands via a crafted Zip file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29637
- https://github.com/mindoc-org/mindoc/issues/788
- github.com/mindoc-org/mindoc
