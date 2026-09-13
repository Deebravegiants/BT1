# [M] CVE-2017-6838

## Summary
Severity: Medium
Advisory: CVE-2017-6838
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2017-6838
Type: osv

## Details
Integer overflow in sfcommands/sfconvert.c in Audio File Library (aka audiofile) 0.3.6 allows remote attackers to cause a denial of service (crash) via a crafted file.

## References
- http://www.debian.org/security/2017/dsa-3814
- http://www.openwall.com/lists/oss-security/2017/03/13/9
- https://blogs.gentoo.org/ago/2017/02/20/audiofile-multiple-ubsan-crashes/
- https://github.com/antlarr/audiofile/commit/7d65f89defb092b63bcbc5d98349fb222ca73b3c
- https://github.com/mpruett/audiofile/issues/41
