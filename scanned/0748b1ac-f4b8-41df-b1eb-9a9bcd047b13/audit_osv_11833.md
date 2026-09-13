# [H] CVE-2017-9993

## Summary
Severity: High
Advisory: CVE-2017-9993
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/CVE-2017-9993
Type: osv

## Details
FFmpeg before 2.8.12, 3.0.x and 3.1.x before 3.1.9, 3.2.x before 3.2.6, and 3.3.x before 3.3.2 does not properly restrict HTTP Live Streaming filename extensions and demuxer names, which allows attackers to read arbitrary files via crafted playlist data.

## References
- http://www.debian.org/security/2017/dsa-3957
- http://www.securityfocus.com/bid/99315
- https://lists.debian.org/debian-lts-announce/2019/01/msg00006.html
- https://github.com/FFmpeg/FFmpeg/commit/189ff4219644532bdfa7bab28dfedaee4d6d4021
- https://github.com/FFmpeg/FFmpeg/commit/a5d849b149ca67ced2d271dc84db0bc95a548abb
