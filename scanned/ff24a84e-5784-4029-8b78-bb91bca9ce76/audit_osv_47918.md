# [H] CVE-2017-14976

## Summary
Severity: High
Advisory: CVE-2017-14976
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-02
Source: https://osv.dev/vulnerability/CVE-2017-14976
Type: osv

## Details
The FoFiType1C::convertToType0 function in FoFiType1C.cc in Poppler 0.59.0 has a heap-based buffer over-read vulnerability if an out-of-bounds font dictionary index is encountered, which allows an attacker to launch a denial of service attack.

## References
- https://lists.debian.org/debian-lts-announce/2017/11/msg00023.html
- https://www.debian.org/security/2018/dsa-4079
- https://bugzilla.freedesktop.org/show_bug.cgi?id=102724
- https://cgit.freedesktop.org/poppler/poppler/commit/?id=da63c35549e8852a410946ab016a3f25ac701bdf
