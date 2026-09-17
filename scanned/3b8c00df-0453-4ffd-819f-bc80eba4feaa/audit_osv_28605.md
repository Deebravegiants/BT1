# [H] CVE-2024-35365

## Summary
Severity: High
Advisory: CVE-2024-35365
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-01-03
Source: https://osv.dev/vulnerability/CVE-2024-35365
Type: osv

## Details
FFmpeg version n6.1.1 has a double-free vulnerability in the fftools/ffmpeg_mux_init.c component of FFmpeg, specifically within the new_stream_audio function.

## References
- https://gist.github.com/1047524396/d7d4ea8055b75c4a9f9bbcff31d21423
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/fftools/ffmpeg_mux_init.c#L886
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35365.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35365
- https://github.com/ffmpeg/ffmpeg/commit/ced5c5fdb8634d39ca9472a2026b2d2fea16c4e5
