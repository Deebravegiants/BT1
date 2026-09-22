# [M] An integer overflow in the component `/libavformat/westwood_vqa.c` of FFmpeg n6.1.1 allows attackers...

## Summary
Severity: Medium
Advisory: JLSEC-2025-139
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-139
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=6.1.1+0 <6.1.2+0

## Details
An integer overflow in the component `/libavformat/westwood_vqa.c` of FFmpeg n6.1.1 allows attackers to cause a denial of service in the application via a crafted VQA file.

## References
- https://gist.github.com/1047524396/ded3e1509d8296ec4a91817867d108e0
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavformat/westwood_vqa.c#L265
- https://github.com/ffmpeg/ffmpeg/commit/86f73277bf014e2ce36dd2594f1e0fb8b3bd6661
