# [M] CVE-2017-6832

## Summary
Severity: Medium
Advisory: CVE-2017-6832
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2017-6832
Type: osv

## Details
Heap-based buffer overflow in the decodeBlock in MSADPCM.cpp in Audio File Library (aka audiofile) 0.3.6, 0.3.5, 0.3.4, 0.3.3, 0.3.2, 0.3.1, 0.3.0, 0.2.7 allows remote attackers to cause a denial of service (crash) via a crafted file.

## References
- http://www.debian.org/security/2017/dsa-3814
- http://www.openwall.com/lists/oss-security/2017/03/13/4
- http://www.securityfocus.com/bid/97589
- https://blogs.gentoo.org/ago/2017/02/20/audiofile-heap-based-buffer-overflow-in-msadpcmdecodeblock-msadpcm-cpp/
- https://github.com/mpruett/audiofile/issues/36
- https://github.com/mpruett/audiofile/pull/42
