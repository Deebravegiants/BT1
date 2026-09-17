# [C] FFmpeg before 8.1 has an integer overflow and resultant out-of-bounds write via CENC (Common...

## Summary
Severity: Critical
Advisory: JLSEC-2026-652
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/JLSEC-2026-652
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <8.1.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <8.1.0+0
- Julia: `FFplay_jll` — affected >=0 <8.1.2+0

## Details
FFmpeg before 8.1 has an integer overflow and resultant out-of-bounds write via CENC (Common Encryption) subsample data to `libavformat/mov.c`.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/22348
- https://github.com/advisories/GHSA-48wr-p98v-9w5h
- https://nvd.nist.gov/vuln/detail/CVE-2026-40962
