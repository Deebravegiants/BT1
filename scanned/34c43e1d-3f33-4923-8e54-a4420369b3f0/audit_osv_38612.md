# [M] CVE-2026-40962

## Summary
Severity: Medium
Advisory: CVE-2026-40962
CVSS: 4.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-40962
Type: osv

## Details
FFmpeg before 8.1 has an integer overflow and resultant out-of-bounds write via CENC (Common Encryption) subsample data to libavformat/mov.c.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/22348
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40962.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40962
