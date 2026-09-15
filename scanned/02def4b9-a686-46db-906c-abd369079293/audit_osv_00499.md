# [H] ALPINE-CVE-2017-14225

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-14225
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14225
Type: osv

## Affected
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.1.11-r0
- Alpine:v3.5: `ffmpeg` — affected >=0 <3.1.11-r0
- Alpine:v3.6: `ffmpeg` — affected >=0 <3.2.8-r0
- Alpine:v3.7: `ffmpeg` — affected >=0 <3.3.4-r0

## Details
The av_color_primaries_name function in libavutil/pixdesc.c in FFmpeg 3.3.3 may return a NULL pointer depending on a value contained in a file, but callers do not anticipate this, as demonstrated by the avcodec_string function in libavcodec/utils.c, leading to a NULL pointer dereference. (It is also conceivable that there is security relevance for a NULL pointer dereference in av_color_primaries_name calls within the ffprobe command-line program.)

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14225
