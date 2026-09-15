# [M] CVE-2017-14059

## Summary
Severity: Medium
Advisory: CVE-2017-14059
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-31
Source: https://osv.dev/vulnerability/CVE-2017-14059
Type: osv

## Details
In FFmpeg 3.3.3, a DoS in cine_read_header() due to lack of an EOF check might cause huge CPU and memory consumption. When a crafted CINE file, which claims a large "duration" field in the header but does not contain sufficient backing data, is provided, the image-offset parsing loop would consume huge CPU and memory resources, since there is no EOF check inside the loop.

## References
- http://www.securityfocus.com/bid/100631
- http://www.debian.org/security/2017/dsa-3996
- https://github.com/FFmpeg/FFmpeg/commit/7e80b63ecd259d69d383623e75b318bf2bd491f6
