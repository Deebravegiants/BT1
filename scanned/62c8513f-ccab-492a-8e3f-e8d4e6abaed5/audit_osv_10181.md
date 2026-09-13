# [M] CVE-2017-14170

## Summary
Severity: Medium
Advisory: CVE-2017-14170
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-07
Source: https://osv.dev/vulnerability/CVE-2017-14170
Type: osv

## Details
In libavformat/mxfdec.c in FFmpeg 3.3.3 -> 2.4, a DoS in mxf_read_index_entry_array() due to lack of an EOF (End of File) check might cause huge CPU consumption. When a crafted MXF file, which claims a large "nb_index_entries" field in the header but does not contain sufficient backing data, is provided, the loop would consume huge CPU resources, since there is no EOF check inside the loop. Moreover, this big loop can be invoked multiple times if there is more than one applicable data segment in the crafted MXF file.

## References
- http://www.securityfocus.com/bid/100700
- https://lists.debian.org/debian-lts-announce/2019/01/msg00006.html
- http://www.debian.org/security/2017/dsa-3996
- https://github.com/FFmpeg/FFmpeg/commit/900f39692ca0337a98a7cf047e4e2611071810c2
- https://github.com/FFmpeg/FFmpeg/commit/f173cdfe669556aa92857adafe60cbe5f2aa1210
