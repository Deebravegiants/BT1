# [M] CVE-2018-13303

## Summary
Severity: Medium
Advisory: CVE-2018-13303
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-05
Source: https://osv.dev/vulnerability/CVE-2018-13303
Type: osv

## Details
In FFmpeg 4.0.1, a missing check for failure of a call to init_get_bits8() in the avpriv_ac3_parse_header function in libavcodec/ac3_parser.c may trigger a NULL pointer dereference while converting a crafted AVI file to MPEG4, leading to a denial of service.

## References
- http://www.securityfocus.com/bid/104675
- https://github.com/FFmpeg/FFmpeg/commit/00e8181bd97c834fe60751b0c511d4bb97875f78
