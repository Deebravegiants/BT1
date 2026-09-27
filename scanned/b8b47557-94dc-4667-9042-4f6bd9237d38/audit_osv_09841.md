# [H] CVE-2017-11665

## Summary
Severity: High
Advisory: CVE-2017-11665
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-27
Source: https://osv.dev/vulnerability/CVE-2017-11665
Type: osv

## Details
The ff_amf_get_field_value function in libavformat/rtmppkt.c in FFmpeg 3.3.2 allows remote RTMP servers to cause a denial of service (Segmentation Violation and application crash) via a crafted stream.

## References
- http://www.debian.org/security/2017/dsa-3957
- http://www.securityfocus.com/bid/100017
- https://github.com/FFmpeg/FFmpeg/commit/ffcc82219cef0928bed2d558b19ef6ea35634130
