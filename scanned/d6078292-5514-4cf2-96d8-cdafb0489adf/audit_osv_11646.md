# [M] CVE-2017-9210

## Summary
Severity: Medium
Advisory: CVE-2017-9210
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/CVE-2017-9210
Type: osv

## Details
libqpdf.a in QPDF 6.0.0 allows remote attackers to cause a denial of service (infinite recursion and stack consumption) via a crafted PDF document, related to unparse functions, aka qpdf-infiniteloop3.

## References
- https://blogs.gentoo.org/ago/2017/05/21/qpdf-three-infinite-loop-in-libqpdf/
- https://usn.ubuntu.com/3638-1/
