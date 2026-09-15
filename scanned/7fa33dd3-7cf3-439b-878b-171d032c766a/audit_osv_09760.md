# [H] CVE-2017-11399

## Summary
Severity: High
Advisory: CVE-2017-11399
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-11399
Type: osv

## Details
Integer overflow in the ape_decode_frame function in libavcodec/apedec.c in FFmpeg 2.4 through 3.3.2 allows remote attackers to cause a denial of service (out-of-array access and application crash) or possibly have unspecified other impact via a crafted APE file.

## References
- http://www.securityfocus.com/bid/100019
- http://www.debian.org/security/2017/dsa-3957
- https://github.com/FFmpeg/FFmpeg/commit/96349da5ec8eda9f0368446e557fe0c8ba0e66b7
- https://github.com/FFmpeg/FFmpeg/commit/ba4beaf6149f7241c8bd85fe853318c2f6837ad0
