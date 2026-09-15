# [H] CVE-2014-9630

## Summary
Severity: High
Advisory: CVE-2014-9630
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-24
Source: https://osv.dev/vulnerability/CVE-2014-9630
Type: osv

## Details
The rtp_packetize_xiph_config function in modules/stream_out/rtpfmt.c in VideoLAN VLC media player before 2.1.6 uses a stack-allocation approach with a size determined by arbitrary input data, which allows remote attackers to cause a denial of service (memory corruption) or possibly have unspecified other impact via a crafted length value.

## References
- http://openwall.com/lists/oss-security/2015/01/20/5
- https://github.com/videolan/vlc/commit/204291467724867b79735c0ee3aeb0dbc2200f97
- https://www.videolan.org/security/sa1501.html
- http://openwall.com/lists/oss-security/2015/01/20/5
- http://openwall.com/lists/oss-security/2015/01/20/5
- https://github.com/videolan/vlc/commit/204291467724867b79735c0ee3aeb0dbc2200f97
