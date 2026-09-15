# [H] CVE-2017-14169

## Summary
Severity: High
Advisory: CVE-2017-14169
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-07
Source: https://osv.dev/vulnerability/CVE-2017-14169
Type: osv

## Details
In the mxf_read_primer_pack function in libavformat/mxfdec.c in FFmpeg 3.3.3 -> 2.4, an integer signedness error might occur when a crafted file, which claims a large "item_num" field such as 0xffffffff, is provided. As a result, the variable "item_num" turns negative, bypassing the check for a large value.

## References
- http://www.debian.org/security/2017/dsa-3996
- http://www.securityfocus.com/bid/100692
- https://lists.debian.org/debian-lts-announce/2019/02/msg00005.html
- https://github.com/FFmpeg/FFmpeg/commit/9d00fb9d70ee8c0cc7002b89318c5be00f1bbdad
- https://github.com/FFmpeg/FFmpeg/commit/a4e85b2e1c8d5b4bf0091157bbdeb0e457fb7b8f
