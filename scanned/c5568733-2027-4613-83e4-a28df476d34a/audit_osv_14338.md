# [M] CVE-2018-9165

## Summary
Severity: Medium
Advisory: CVE-2018-9165
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-01
Source: https://osv.dev/vulnerability/CVE-2018-9165
Type: osv

## Details
The pushdup function in util/decompile.c in libming through 0.4.8 does not recognize the need for ActionPushDuplicate to perform a deep copy when a String is at the top of the stack, making the library vulnerable to a util/decompile.c getName NULL pointer dereference, which may allow attackers to cause a denial of service via a crafted SWF file.

## References
- https://lists.debian.org/debian-lts-announce/2018/04/msg00008.html
- https://github.com/libming/libming/issues/121
