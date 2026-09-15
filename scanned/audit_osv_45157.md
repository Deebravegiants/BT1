# [C] FFmpeg n6.1.1 is Integer Overflow

## Summary
Severity: Critical
Advisory: JLSEC-2025-140
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-140
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=6.1.1+0 <6.1.2+0

## Details
FFmpeg n6.1.1 is Integer Overflow. The vulnerability exists in the `parse_options` function of sbgdec.c within the libavformat module. When parsing certain options, the software does not adequately validate the input. This allows for negative duration values to be accepted without proper bounds checking.

## References
- https://gist.github.com/1047524396/1e72f170d58c2547ebd4db4cdf6cfabf
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavformat/sbgdec.c#L389
- https://github.com/ffmpeg/ffmpeg/commit/0bed22d597b78999151e3bde0768b7fe763fc2a6
