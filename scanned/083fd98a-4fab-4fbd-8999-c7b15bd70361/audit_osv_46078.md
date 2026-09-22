# [H] An out-of-bounds write vulnerability in FFmpeg's libavcodec library, specifically in the MagicYUV...

## Summary
Severity: High
Advisory: JLSEC-2026-653
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/JLSEC-2026-653
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <8.1.2+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <8.1.2+0
- Julia: `FFplay_jll` — affected >=0 <8.1.2+0

## Details
An out-of-bounds write vulnerability in FFmpeg's libavcodec library, specifically in the MagicYUV decoder, allows denial-of-service and, in some cases, can be exploited for remote code execution.

This vulnerability is associated with the file `libavcodec/magicyuv.C`.

This issue affects FFmpeg before version 8.1.2.

## References
- https://access.redhat.com/security/cve/CVE-2026-8461
- https://bugzilla.redhat.com/show_bug.cgi?id=2490308
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23159
- https://github.com/advisories/GHSA-qff7-4q6c-m8h6
- https://nvd.nist.gov/vuln/detail/CVE-2026-8461
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-8461.json
