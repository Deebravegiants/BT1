# [H] CVE-2017-17670

## Summary
Severity: High
Advisory: CVE-2017-17670
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-15
Source: https://osv.dev/vulnerability/CVE-2017-17670
Type: osv

## Details
In VideoLAN VLC media player through 2.2.8, there is a type conversion vulnerability in modules/demux/mp4/libmp4.c in the MP4 demux module leading to a invalid free, because the type of a box may be changed between a read operation and a free operation.

## References
- http://www.securityfocus.com/bid/102214
- http://www.securitytracker.com/id/1040938
- https://www.debian.org/security/2018/dsa-4203
- http://openwall.com/lists/oss-security/2017/12/15/1
