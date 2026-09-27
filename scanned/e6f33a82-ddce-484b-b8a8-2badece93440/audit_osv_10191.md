# [H] CVE-2017-14225

## Summary
Severity: High
Advisory: CVE-2017-14225
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-09
Source: https://osv.dev/vulnerability/CVE-2017-14225
Type: osv

## Details
The av_color_primaries_name function in libavutil/pixdesc.c in FFmpeg 3.3.3 may return a NULL pointer depending on a value contained in a file, but callers do not anticipate this, as demonstrated by the avcodec_string function in libavcodec/utils.c, leading to a NULL pointer dereference. (It is also conceivable that there is security relevance for a NULL pointer dereference in av_color_primaries_name calls within the ffprobe command-line program.)

## References
- http://www.debian.org/security/2017/dsa-3996
- http://www.securityfocus.com/bid/100704
- https://github.com/FFmpeg/FFmpeg/commit/837cb4325b712ff1aab531bf41668933f61d75d2
- https://lists.ffmpeg.org/pipermail/ffmpeg-devel/2017-August/215198.html
