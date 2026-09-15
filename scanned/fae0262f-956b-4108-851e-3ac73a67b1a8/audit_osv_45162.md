# [M] FFmpeg n6.1.1 has a vulnerability in the DXA demuxer of the libavformat library allowing for an...

## Summary
Severity: Medium
Advisory: JLSEC-2025-145
Ecosystem: Julia
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-145
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=6.1.1+0 <6.1.2+0

## Details
FFmpeg n6.1.1 has a vulnerability in the DXA demuxer of the libavformat library allowing for an integer overflow, potentially resulting in a denial-of-service (DoS) condition or other undefined behavior.

## References
- https://gist.github.com/1047524396/0f4d90ef87553f772f888223085ac806
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavformat/dxa.c#L125
- https://github.com/ffmpeg/ffmpeg/commit/50d8e4f27398fd5778485a827d7a2817921f8540
