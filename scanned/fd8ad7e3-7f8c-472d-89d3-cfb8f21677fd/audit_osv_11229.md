# [M] CVE-2017-6835

## Summary
Severity: Medium
Advisory: CVE-2017-6835
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2017-6835
Type: osv

## Details
The reset1 function in libaudiofile/modules/BlockCodec.cpp in Audio File Library (aka audiofile) 0.3.6 allows remote attackers to cause a denial of service (divide-by-zero error and crash) via a crafted file.

## References
- http://www.debian.org/security/2017/dsa-3814
- http://www.openwall.com/lists/oss-security/2017/03/13/7
- https://blogs.gentoo.org/ago/2017/02/20/audiofile-divide-by-zero-in-blockcodecreset1-blockcodec-cpp/
- https://github.com/mpruett/audiofile/issues/39
- https://github.com/mpruett/audiofile/pull/42
