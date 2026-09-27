# [M] CVE-2018-5294

## Summary
Severity: Medium
Advisory: CVE-2018-5294
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-08
Source: https://osv.dev/vulnerability/CVE-2018-5294
Type: osv

## Details
In libming 0.4.8, there is an integer overflow (caused by an out-of-range left shift) in the readUInt32 function (util/read.c). Remote attackers could leverage this vulnerability to cause a denial-of-service via a crafted swf file.

## References
- https://github.com/libming/libming/issues/98
- https://lists.debian.org/debian-lts-announce/2018/03/msg00008.html
- https://security.gentoo.org/glsa/201904-24
