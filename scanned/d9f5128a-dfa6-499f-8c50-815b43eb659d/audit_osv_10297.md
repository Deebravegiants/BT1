# [H] CVE-2017-14767

## Summary
Severity: High
Advisory: CVE-2017-14767
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-27
Source: https://osv.dev/vulnerability/CVE-2017-14767
Type: osv

## Details
The sdp_parse_fmtp_config_h264 function in libavformat/rtpdec_h264.c in FFmpeg before 3.3.4 mishandles empty sprop-parameter-sets values, which allows remote attackers to cause a denial of service (heap buffer overflow) or possibly have unspecified other impact via a crafted sdp file.

## References
- https://lists.debian.org/debian-lts-announce/2019/01/msg00006.html
- http://www.debian.org/security/2017/dsa-3996
- http://www.securityfocus.com/bid/101019
- https://github.com/FFmpeg/FFmpeg/commit/c42a1388a6d1bfd8001bf6a4241d8ca27e49326d
