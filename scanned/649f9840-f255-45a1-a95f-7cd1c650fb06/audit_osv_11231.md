# [M] CVE-2017-6837

## Summary
Severity: Medium
Advisory: CVE-2017-6837
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2017-6837
Type: osv

## Details
WAVE.cpp in Audio File Library (aka audiofile) 0.3.6 allows remote attackers to cause a denial of service (crash) via vectors related to a large number of coefficients.

## References
- http://www.securityfocus.com/bid/97314
- http://www.debian.org/security/2017/dsa-3814
- http://www.openwall.com/lists/oss-security/2017/03/13/9
- https://blogs.gentoo.org/ago/2017/02/20/audiofile-multiple-ubsan-crashes/
- https://github.com/antlarr/audiofile/commit/c48e4c6503f7dabd41f11d4c9c7b7f8960e7f2c0
- https://github.com/mpruett/audiofile/issues/41
