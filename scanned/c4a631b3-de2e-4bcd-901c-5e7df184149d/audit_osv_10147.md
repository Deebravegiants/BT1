# [M] CVE-2017-14057

## Summary
Severity: Medium
Advisory: CVE-2017-14057
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-31
Source: https://osv.dev/vulnerability/CVE-2017-14057
Type: osv

## Details
In FFmpeg 3.3.3, a DoS in asf_read_marker() due to lack of an EOF (End of File) check might cause huge CPU and memory consumption. When a crafted ASF file, which claims a large "name_len" or "count" field in the header but does not contain sufficient backing data, is provided, the loops over the name and markers would consume huge CPU and memory resources, since there is no EOF check inside these loops.

## References
- http://www.securityfocus.com/bid/100630
- https://lists.debian.org/debian-lts-announce/2019/01/msg00006.html
- http://www.debian.org/security/2017/dsa-3996
- https://github.com/FFmpeg/FFmpeg/commit/7f9ec5593e04827249e7aeb466da06a98a0d7329
