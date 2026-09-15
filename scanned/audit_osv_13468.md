# [M] CVE-2018-1999015

## Summary
Severity: Medium
Advisory: CVE-2018-1999015
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-1999015
Type: osv

## Details
FFmpeg before commit 5aba5b89d0b1d73164d3b81764828bb8b20ff32a contains an out of array read vulnerability in ASF_F format demuxer that can result in heap memory reading. This attack appear to be exploitable via specially crafted ASF file that has to provided as input. This vulnerability appears to have been fixed in 5aba5b89d0b1d73164d3b81764828bb8b20ff32a and later.

## References
- http://www.securityfocus.com/bid/104896
- https://github.com/FFmpeg/FFmpeg/commit/5aba5b89d0b1d73164d3b81764828bb8b20ff32a
