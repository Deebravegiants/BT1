# [M] CVE-2017-14171

## Summary
Severity: Medium
Advisory: CVE-2017-14171
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-07
Source: https://osv.dev/vulnerability/CVE-2017-14171
Type: osv

## Details
In libavformat/nsvdec.c in FFmpeg 2.4 and 3.3.3, a DoS in nsv_parse_NSVf_header() due to lack of an EOF (End of File) check might cause huge CPU consumption. When a crafted NSV file, which claims a large "table_entries_used" field in the header but does not contain sufficient backing data, is provided, the loop over 'table_entries_used' would consume huge CPU resources, since there is no EOF check inside the loop.

## References
- http://www.securityfocus.com/bid/100706
- https://lists.debian.org/debian-lts-announce/2019/01/msg00006.html
- http://www.debian.org/security/2017/dsa-3996
- https://github.com/FFmpeg/FFmpeg/commit/c24bcb553650b91e9eff15ef6e54ca73de2453b7
