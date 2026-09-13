# [M] CVE-2017-9988

## Summary
Severity: Medium
Advisory: CVE-2017-9988
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/CVE-2017-9988
Type: osv

## Details
The readEncUInt30 function in util/read.c in libming 0.4.8 mishandles memory allocation. A crafted input will lead to a remote denial of service (NULL pointer dereference) attack against parser.c.

## References
- https://lists.debian.org/debian-lts-announce/2017/11/msg00022.html
- https://security.gentoo.org/glsa/201904-24
- https://github.com/libming/libming/issues/85
