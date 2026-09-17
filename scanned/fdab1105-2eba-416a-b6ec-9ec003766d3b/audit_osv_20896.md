# [C] CVE-2021-38171

## Summary
Severity: Critical
Advisory: CVE-2021-38171
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-21
Source: https://osv.dev/vulnerability/CVE-2021-38171
Type: osv

## Details
adts_decode_extradata in libavformat/adtsenc.c in FFmpeg 4.4 does not check the init_get_bits return value, which is a necessary step because the second argument to init_get_bits can be crafted.

## References
- https://patchwork.ffmpeg.org/project/ffmpeg/patch/AS8P193MB12542A86E22F8207EC971930B6F19%40AS8P193MB1254.EURP193.PROD.OUTLOOK.COM/
- https://lists.debian.org/debian-lts-announce/2021/11/msg00012.html
- https://security.gentoo.org/glsa/202312-14
- https://www.debian.org/security/2021/dsa-4990
- https://www.debian.org/security/2021/dsa-4998
- https://github.com/FFmpeg/FFmpeg/commit/9ffa49496d1aae4cbbb387aac28a9e061a6ab0a6
