# [M] libheif vulnerable to segmentation fault via floating point exception

## Summary
Severity: Medium
Advisory: GHSA-22fx-6r9m-r8h9
CVE: CVE-2023-29659
CWE: CWE-369
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-05
Source: https://github.com/advisories/GHSA-22fx-6r9m-r8h9
Type: github-advisory

## Affected
- Go: `github.com/strukturag/libheif` — affected >=0 <1.15.2

## Details
A Segmentation fault caused by a floating point exception exists in libheif 1.15.1 using crafted heif images via the heif::Fraction::round() function in box.cc, which causes a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29659
- https://github.com/strukturag/libheif/issues/794
- https://github.com/strukturag/libheif/commit/e05e15b57a38ec411cb9acb38512a1c36ff62991
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CKAE6NQBA3Q7GS6VTNDZRZZZVPPEFUEZ
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LGKHDCS4HRZE3UGXYYDYPTIPNIBRLQ5L
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CKAE6NQBA3Q7GS6VTNDZRZZZVPPEFUEZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LGKHDCS4HRZE3UGXYYDYPTIPNIBRLQ5L
- github.com/strukturag/libheif
