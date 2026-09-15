# [C] CVE-2017-1000158

## Summary
Severity: Critical
Advisory: CVE-2017-1000158
Aliases: PSF-2017-6
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-17
Source: https://osv.dev/vulnerability/CVE-2017-1000158
Type: osv

## Details
CPython (aka Python) up to 2.7.13 is vulnerable to an integer overflow in the PyString_DecodeEscape function in stringobject.c, resulting in heap-based buffer overflow (and possible arbitrary code execution)

## References
- http://www.securitytracker.com/id/1039890
- https://lists.debian.org/debian-lts-announce/2017/11/msg00035.html
- https://lists.debian.org/debian-lts-announce/2017/11/msg00036.html
- https://lists.debian.org/debian-lts-announce/2018/09/msg00030.html
- https://lists.debian.org/debian-lts-announce/2018/09/msg00031.html
- https://security.gentoo.org/glsa/201805-02
- https://security.netapp.com/advisory/ntap-20230216-0001/
- https://www.debian.org/security/2018/dsa-4307
- https://bugs.python.org/issue30657
