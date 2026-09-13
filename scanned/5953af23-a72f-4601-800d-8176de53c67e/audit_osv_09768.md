# [M] CVE-2017-11423

## Summary
Severity: Medium
Advisory: CVE-2017-11423
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-18
Source: https://osv.dev/vulnerability/CVE-2017-11423
Type: osv

## Details
The cabd_read_string function in mspack/cabd.c in libmspack 0.5alpha, as used in ClamAV 0.99.2 and other products, allows remote attackers to cause a denial of service (stack-based buffer over-read and application crash) via a crafted CAB file.

## References
- https://lists.debian.org/debian-lts-announce/2018/02/msg00014.html
- http://www.debian.org/security/2017/dsa-3946
- https://github.com/hackerlib/hackerlib-vul/tree/master/clamav-vul
- https://security.gentoo.org/glsa/201804-16
- https://bugzilla.clamav.net/show_bug.cgi?id=11873
