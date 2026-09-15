# [H] CVE-2017-6419

## Summary
Severity: High
Advisory: CVE-2017-6419
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/CVE-2017-6419
Type: osv

## Details
mspack/lzxd.c in libmspack 0.5alpha, as used in ClamAV 0.99.2, allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted CHM file.

## References
- https://lists.debian.org/debian-lts-announce/2018/02/msg00014.html
- http://www.debian.org/security/2017/dsa-3946
- https://github.com/varsleak/varsleak-vul/blob/master/clamav-vul/heap-overflow/clamav_chm_crash.md
- https://security.gentoo.org/glsa/201804-16
- https://bugzilla.clamav.net/show_bug.cgi?id=11701
- https://github.com/vrtadmin/clamav-devel/commit/a83773682e856ad6529ba6db8d1792e6d515d7f1
