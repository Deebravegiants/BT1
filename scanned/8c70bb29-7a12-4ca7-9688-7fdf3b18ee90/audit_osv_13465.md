# [M] CVE-2018-1999012

## Summary
Severity: Medium
Advisory: CVE-2018-1999012
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-1999012
Type: osv

## Details
FFmpeg before commit 9807d3976be0e92e4ece3b4b1701be894cd7c2e1 contains a CWE-835: Infinite loop vulnerability in pva format demuxer that can result in a Vulnerability that allows attackers to consume excessive amount of resources like CPU and RAM. This attack appear to be exploitable via specially crafted PVA file has to be provided as input. This vulnerability appears to have been fixed in 9807d3976be0e92e4ece3b4b1701be894cd7c2e1 and later.

## References
- https://lists.debian.org/debian-lts-announce/2019/03/msg00041.html
- http://www.securityfocus.com/bid/104896
- https://github.com/FFmpeg/FFmpeg/commit/9807d3976be0e92e4ece3b4b1701be894cd7c2e1
