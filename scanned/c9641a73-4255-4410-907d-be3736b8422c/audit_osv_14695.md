# [M] CVE-2019-10873

## Summary
Severity: Medium
Advisory: CVE-2019-10873
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-05
Source: https://osv.dev/vulnerability/CVE-2019-10873
Type: osv

## Details
An issue was discovered in Poppler 0.74.0. There is a NULL pointer dereference in the function SplashClip::clipAALine at splash/SplashClip.cc.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7MAWV24KRXTFODLVT46RXI27XIQFX2QR/
- https://usn.ubuntu.com/4042-1/
- http://www.securityfocus.com/bid/107862
- https://gitlab.freedesktop.org/poppler/poppler/issues/748
