# [M] CVE-2017-16898

## Summary
Severity: Medium
Advisory: CVE-2017-16898
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-11-20
Source: https://osv.dev/vulnerability/CVE-2017-16898
Type: osv

## Details
The printMP3Headers function in util/listmp3.c in libming v0.4.8 or earlier is vulnerable to a global buffer overflow, which may allow attackers to cause a denial of service via a crafted file, a different vulnerability than CVE-2016-9264.

## References
- https://lists.debian.org/debian-lts-announce/2018/01/msg00014.html
- https://github.com/libming/libming/issues/75
