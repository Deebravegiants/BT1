# [H] Goutil vulnerable to path traversal when unzipping files

## Summary
Severity: High
Advisory: GHSA-fx2v-qfhr-4chv
CVE: CVE-2023-27475
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-07
Source: https://github.com/advisories/GHSA-fx2v-qfhr-4chv
Type: github-advisory

## Affected
- Go: `github.com/gookit/goutil` — affected >=0 <0.6.0

## Details
### Impact

ZipSlip issue when use fsutil package to unzip files.
When users use fsutil.Unzip to unzip zip files from a malicious attacker, they may be vulnerable to path traversal. 

### Patches

It has been fixed in v0.6.0, Please upgrade version to v0.6.0 or above.

### Workarounds
No, users have to upgrade version.

## References
- https://github.com/gookit/goutil/security/advisories/GHSA-fx2v-qfhr-4chv
- https://nvd.nist.gov/vuln/detail/CVE-2023-27475
- https://github.com/gookit/goutil/commit/d7b94fede71f018f129f7d21feb58c895d28dadc
- https://github.com/gookit/goutil
- https://pkg.go.dev/vuln/GO-2023-1611
- https://security.netapp.com/advisory/ntap-20230427-0003
