# [M] CVE-2020-13904

## Summary
Severity: Medium
Advisory: CVE-2020-13904
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-06-07
Source: https://osv.dev/vulnerability/CVE-2020-13904
Type: osv

## Details
FFmpeg 2.8 and 4.2.3 has a use-after-free via a crafted EXTINF duration in an m3u8 file because parse_playlist in libavformat/hls.c frees a pointer, and later that pointer is accessed in av_probe_input_format3 in libavformat/format.c.

## References
- https://patchwork.ffmpeg.org/project/ffmpeg/patch/20200529033905.41926-1-lq%40chinaffmpeg.org/
- https://lists.debian.org/debian-lts-announce/2020/07/msg00022.html
- https://security.gentoo.org/glsa/202007-58
- https://usn.ubuntu.com/4431-1/
- https://www.debian.org/security/2020/dsa-4722
- https://trac.ffmpeg.org/ticket/8673
- https://github.com/FFmpeg/FFmpeg/commit/6959358683c7533f586c07a766acc5fe9544d8b2
