# [H] CVE-2018-13305

## Summary
Severity: High
Advisory: CVE-2018-13305
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-07-05
Source: https://osv.dev/vulnerability/CVE-2018-13305
Type: osv

## Details
In FFmpeg 4.0.1, due to a missing check for negative values of the mquant variable, the vc1_put_blocks_clamped function in libavcodec/vc1_block.c may trigger an out-of-array access while converting a crafted AVI file to MPEG4, leading to an information disclosure or a denial of service.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00012.html
- https://github.com/FFmpeg/FFmpeg/commit/d08d4a8c7387e758d439b0592782e4cfa2b4d6a4
