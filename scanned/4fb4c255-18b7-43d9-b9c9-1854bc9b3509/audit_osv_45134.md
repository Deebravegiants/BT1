# [C] `adts_decode_extradata` in `libavformat/adtsenc.c` in FFmpeg 4.4 does not check the `init_get_bits`...

## Summary
Severity: Critical
Advisory: JLSEC-2025-118
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-118
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=4.4.0+0 <4.4.2+0

## Details
`adts_decode_extradata` in `libavformat/adtsenc.c` in FFmpeg 4.4 does not check the `init_get_bits` return value, which is a necessary step because the second argument to `init_get_bits` can be crafted.

## References
- https://github.com/FFmpeg/FFmpeg/commit/9ffa49496d1aae4cbbb387aac28a9e061a6ab0a6
- https://lists.debian.org/debian-lts-announce/2021/11/msg00012.html
- https://patchwork.ffmpeg.org/project/ffmpeg/patch/AS8P193MB12542A86E22F8207EC971930B6F19%40AS8P193MB1254.EURP193.PROD.OUTLOOK.COM/
- https://security.gentoo.org/glsa/202312-14
- https://www.debian.org/security/2021/dsa-4990
- https://www.debian.org/security/2021/dsa-4998
