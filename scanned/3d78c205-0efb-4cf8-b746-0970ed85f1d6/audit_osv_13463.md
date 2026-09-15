# [C] CVE-2018-1999010

## Summary
Severity: Critical
Advisory: CVE-2018-1999010
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-1999010
Type: osv

## Details
FFmpeg before commit cced03dd667a5df6df8fd40d8de0bff477ee02e8 contains multiple out of array access vulnerabilities in the mms protocol that can result in attackers accessing out of bound data. This attack appear to be exploitable via network connectivity. This vulnerability appears to have been fixed in cced03dd667a5df6df8fd40d8de0bff477ee02e8 and later.

## References
- http://www.securityfocus.com/bid/104896
- https://lists.debian.org/debian-lts-announce/2019/01/msg00006.html
- https://github.com/FFmpeg/FFmpeg/commit/cced03dd667a5df6df8fd40d8de0bff477ee02e8
