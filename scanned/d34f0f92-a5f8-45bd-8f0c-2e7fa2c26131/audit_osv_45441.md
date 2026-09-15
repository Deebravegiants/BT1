# [M] FFmpeg's RASC video decoder (decode_dlta in libavcodec/rasc.c) performs 32-bit reads and writes...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1171
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1171
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=0 <9.0.0+0

## Details
FFmpeg's RASC video decoder (`decode_dlta` in `libavcodec/rasc.c`) performs 32-bit reads and writes at the row cursor before the `NEXT_LINE` row-boundary check and validates the DLTA region in pixel rather than byte units, so a DLTA run on a PAL8 frame can access several bytes past the row allocation. A crafted media stream using the RASC FourCC, decoded by libavcodec, triggers a bitstream-controlled out-of-bounds heap write and adjacent out-of-bounds read, leading to memory corruption.

## References
- https://access.redhat.com/errata/RHSA-2026:43711
- https://access.redhat.com/security/cve/CVE-2026-58049
- https://bugzilla.redhat.com/show_bug.cgi?id=2493952
- https://github.com/FFmpeg/FFmpeg/blob/master/libavcodec/rasc.c
- https://github.com/advisories/GHSA-mjxr-6gqf-w78h
- https://github.com/bikini/exploitarium/tree/main/ffmpeg-rasc-dlta-calc-poc
- https://nvd.nist.gov/vuln/detail/CVE-2026-58049
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-58049.json
- https://www.vulncheck.com/advisories/ffmpeg-out-of-bounds-write-in-rasc-decoder-decode-dlta
