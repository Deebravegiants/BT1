# [M] CVE-2017-6839

## Summary
Severity: Medium
Advisory: CVE-2017-6839
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2017-6839
Type: osv

## Details
Integer overflow in modules/MSADPCM.cpp in Audio File Library (aka audiofile) 0.3.6 allows remote attackers to cause a denial of service (crash) via a crafted file.

## References
- http://www.debian.org/security/2017/dsa-3814
- http://www.openwall.com/lists/oss-security/2017/03/13/9
- https://blogs.gentoo.org/ago/2017/02/20/audiofile-multiple-ubsan-crashes/
- https://github.com/antlarr/audiofile/commit/beacc44eb8cdf6d58717ec1a5103c5141f1b37f9
- https://github.com/mpruett/audiofile/issues/41
