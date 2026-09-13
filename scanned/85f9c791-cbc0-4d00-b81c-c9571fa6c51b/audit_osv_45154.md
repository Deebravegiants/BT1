# [M] FFmpeg n6.1.1 has a vulnerability in the AVI demuxer of the libavformat library which allows for an...

## Summary
Severity: Medium
Advisory: JLSEC-2025-137
Ecosystem: Julia
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-137
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=6.1.1+0 <6.1.2+0

## Details
FFmpeg n6.1.1 has a vulnerability in the AVI demuxer of the libavformat library which allows for an integer overflow, potentially resulting in a denial-of-service (DoS) condition.

## References
- https://gist.github.com/1047524396/a148f3679415a6da53ca112eb2ba1523
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavformat/avidec.c#L1699
- https://github.com/ffmpeg/ffmpeg/commit/7a089ed8e049e3bfcb22de1250b86f2106060857
- https://lists.debian.org/debian-lts-announce/2025/02/msg00000.html
