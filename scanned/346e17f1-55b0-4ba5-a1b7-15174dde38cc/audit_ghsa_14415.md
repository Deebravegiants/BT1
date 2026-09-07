# [H] Go-huge-util vulnerable to path traversal when unzipping files

## Summary
Severity: High
Advisory: GHSA-5g39-ppwg-6xx8
CVE: CVE-2023-28105
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2023-03-16
Source: https://github.com/advisories/GHSA-5g39-ppwg-6xx8
Type: github-advisory

## Affected
- Go: `github.com/dablelv/go-huge-util` — affected >=0 <0.0.34

## Details
Impact
ZipSlip issue when use fsutil package to unzip files.
When users use zip.Unzip to unzip zip files from a malicious attacker, they may be vulnerable to path traversal.

Patches
It has been fixed in v0.0.34, Please upgrade version to v0.0.34 or above.

Workarounds
No, users have to upgrade version.

Specific Go Packages Affected
github.com/dablelv/go-huge-util/zip

References

## References
- https://github.com/dablelv/go-huge-util/security/advisories/GHSA-5g39-ppwg-6xx8
- https://nvd.nist.gov/vuln/detail/CVE-2023-28105
- https://github.com/dablelv/go-huge-util/commit/0e308b0fac8973e6fa251b0ab095cdc5c1c0956b
- https://github.com/dablelv/go-huge-util
- https://pkg.go.dev/vuln/GO-2023-1640
