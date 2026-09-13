# [H] CVE-2017-11719

## Summary
Severity: High
Advisory: CVE-2017-11719
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-28
Source: https://osv.dev/vulnerability/CVE-2017-11719
Type: osv

## Details
The dnxhd_decode_header function in libavcodec/dnxhddec.c in FFmpeg 3.0 through 3.3.2 allows remote attackers to cause a denial of service (out-of-array access) or possibly have unspecified other impact via a crafted DNxHD file.

## References
- http://www.debian.org/security/2017/dsa-3957
- http://www.securityfocus.com/bid/100020
- https://github.com/FFmpeg/FFmpeg/commit/296debd213bd6dce7647cedd34eb64e5b94cdc92
- https://github.com/FFmpeg/FFmpeg/commit/f31fc4755f69ab26bf6e8be47875b7dcede8e29e
