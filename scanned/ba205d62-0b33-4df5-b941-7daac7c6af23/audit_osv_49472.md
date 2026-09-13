# [H] CVE-2019-13217

## Summary
Severity: High
Advisory: CVE-2019-13217
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-15
Source: https://osv.dev/vulnerability/CVE-2019-13217
Type: osv

## Details
A heap buffer overflow in the start_decoder function in stb_vorbis through 2019-03-04 allows an attacker to cause a denial of service or execute arbitrary code by opening a crafted Ogg Vorbis file.

## References
- https://lists.debian.org/debian-lts-announce/2023/01/msg00045.html
- http://nothings.org/stb_vorbis/
- https://github.com/nothings/stb/commits/master/stb_vorbis.c
- https://github.com/nothings/stb/commit/98fdfc6df88b1e34a736d5e126e6c8139c8de1a6
