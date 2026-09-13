# [H] CVE-2016-8654

## Summary
Severity: High
Advisory: CVE-2016-8654
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2016-8654
Type: osv

## Details
A heap-buffer overflow vulnerability was found in QMFB code in JPC codec caused by buffer being allocated with too small size. jasper versions before 2.0.0 are affected.

## References
- http://www.securityfocus.com/bid/94583
- https://access.redhat.com/errata/RHSA-2017:1208
- https://www.debian.org/security/2017/dsa-3785
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-8654
- https://github.com/mdadams/jasper/commit/4a59cfaf9ab3d48fca4a15c0d2674bf7138e3d1a
- https://github.com/mdadams/jasper/issues/93
- https://github.com/mdadams/jasper/issues/94
