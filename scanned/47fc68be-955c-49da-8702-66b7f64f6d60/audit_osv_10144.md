# [M] CVE-2017-14054

## Summary
Severity: Medium
Advisory: CVE-2017-14054
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-31
Source: https://osv.dev/vulnerability/CVE-2017-14054
Type: osv

## Details
In libavformat/rmdec.c in FFmpeg 3.3.3, a DoS in ivr_read_header() due to lack of an EOF (End of File) check might cause huge CPU consumption. When a crafted IVR file, which claims a large "len" field in the header but does not contain sufficient backing data, is provided, the first type==4 loop would consume huge CPU resources, since there is no EOF check inside the loop.

## References
- http://www.securityfocus.com/bid/100627
- http://www.debian.org/security/2017/dsa-3996
- https://github.com/FFmpeg/FFmpeg/commit/124eb202e70678539544f6268efc98131f19fa49
