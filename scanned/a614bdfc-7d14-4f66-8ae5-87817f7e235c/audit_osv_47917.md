# [H] CVE-2017-14975

## Summary
Severity: High
Advisory: CVE-2017-14975
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-02
Source: https://osv.dev/vulnerability/CVE-2017-14975
Type: osv

## Details
The FoFiType1C::convertToType0 function in FoFiType1C.cc in Poppler 0.59.0 has a NULL pointer dereference vulnerability because a data structure is not initialized, which allows an attacker to launch a denial of service attack.

## References
- https://lists.debian.org/debian-lts-announce/2017/11/msg00023.html
- https://www.debian.org/security/2018/dsa-4079
- https://bugzilla.freedesktop.org/show_bug.cgi?id=102653
