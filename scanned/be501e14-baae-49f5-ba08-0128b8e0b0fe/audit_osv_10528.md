# [C] CVE-2017-16840

## Summary
Severity: Critical
Advisory: CVE-2017-16840
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-21
Source: https://osv.dev/vulnerability/CVE-2017-16840
Type: osv

## Details
The VC-2 Video Compression encoder in FFmpeg 3.0 and 3.4 allows remote attackers to cause a denial of service (out-of-bounds read) because of incorrect buffer padding for non-Haar wavelets, related to libavcodec/vc2enc.c and libavcodec/vc2enc_dwt.c.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commit%3Bh=a94cb36ab2ad99d3a1331c9f91831ef593d94f74
- http://www.securityfocus.com/bid/101924
- https://www.debian.org/security/2017/dsa-4049
- https://github.com/FFmpeg/FFmpeg/commit/94e538aebbc9f9c529e8b1f2eda860cfb8c473b1
