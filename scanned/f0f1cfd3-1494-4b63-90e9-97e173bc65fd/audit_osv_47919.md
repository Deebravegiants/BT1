# [H] CVE-2017-14977

## Summary
Severity: High
Advisory: CVE-2017-14977
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-02
Source: https://osv.dev/vulnerability/CVE-2017-14977
Type: osv

## Details
The FoFiTrueType::getCFFBlock function in FoFiTrueType.cc in Poppler 0.59.0 has a NULL pointer dereference vulnerability due to lack of validation of a table pointer, which allows an attacker to launch a denial of service attack.

## References
- https://lists.debian.org/debian-lts-announce/2017/11/msg00023.html
- https://www.debian.org/security/2018/dsa-4079
- https://bugs.freedesktop.org/show_bug.cgi?id=103045
