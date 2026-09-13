# [M] CVE-2017-6830

## Summary
Severity: Medium
Advisory: CVE-2017-6830
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2017-6830
Type: osv

## Details
Heap-based buffer overflow in the alaw2linear_buf function in G711.cpp in Audio File Library (aka audiofile) 0.3.6 allows remote attackers to cause a denial of service (crash) via a crafted file.

## References
- http://www.debian.org/security/2017/dsa-3814
- http://www.openwall.com/lists/oss-security/2017/03/13/2
- https://blogs.gentoo.org/ago/2017/02/20/audiofile-heap-based-buffer-overflow-in-alaw2linear_buf-g711-cpp/
- https://github.com/mpruett/audiofile/issues/34
- https://github.com/mpruett/audiofile/pull/42
