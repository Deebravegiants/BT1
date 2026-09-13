# [M] CVE-2019-11026

## Summary
Severity: Medium
Advisory: CVE-2019-11026
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-08
Source: https://osv.dev/vulnerability/CVE-2019-11026
Type: osv

## Details
FontInfoScanner::scanFonts in FontInfo.cc in Poppler 0.75.0 has infinite recursion, leading to a call to the error function in Error.cc.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T5JWQE2WP4W4F2FEYPYJQBPQIOG75MVH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XGYLZZ4DZUDBQEGCNDWSZPSFNNZJF4S6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XWWVIYFXM74KJFIDHP4W67HR4FRF2LDE/
- https://gitlab.freedesktop.org/poppler/poppler/issues/752
- https://research.loginsoft.com/bugs/1508/
