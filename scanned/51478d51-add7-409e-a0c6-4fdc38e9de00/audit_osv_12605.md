# [H] CVE-2018-13302

## Summary
Severity: High
Advisory: CVE-2018-13302
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-05
Source: https://osv.dev/vulnerability/CVE-2018-13302
Type: osv

## Details
In FFmpeg 4.0.1, improper handling of frame types (other than EAC3_FRAME_TYPE_INDEPENDENT) that have multiple independent substreams in the handle_eac3 function in libavformat/movenc.c may trigger an out-of-array access while converting a crafted AVI file to MPEG4, leading to a denial of service or possibly unspecified other impact.

## References
- http://www.securityfocus.com/bid/104675
- https://www.debian.org/security/2018/dsa-4249
- https://github.com/FFmpeg/FFmpeg/commit/ed22dc22216f74c75ee7901f82649e1ff725ba50
