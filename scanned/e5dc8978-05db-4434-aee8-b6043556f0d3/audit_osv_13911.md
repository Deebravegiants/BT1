# [M] CVE-2018-5251

## Summary
Severity: Medium
Advisory: CVE-2018-5251
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-05
Source: https://osv.dev/vulnerability/CVE-2018-5251
Type: osv

## Details
In libming 0.4.8, there is an integer signedness error vulnerability (left shift of a negative value) in the readSBits function (util/read.c). Remote attackers can leverage this vulnerability to cause a denial of service via a crafted swf file.

## References
- https://lists.debian.org/debian-lts-announce/2018/03/msg00008.html
- https://security.gentoo.org/glsa/201904-24
- https://github.com/libming/libming/issues/97
