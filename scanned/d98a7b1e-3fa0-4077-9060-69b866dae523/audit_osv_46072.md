# [H] JLSEC-2026-648

## Summary
Severity: High
Advisory: JLSEC-2026-648
Ecosystem: Julia
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:H/SA:H/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/JLSEC-2026-648
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <8.0.0+0
- Julia: `FFplay_jll` — affected >=0 <8.1.2+0

## Details
A heap-buffer-overflow write exists in jpeg2000dec FFmpeg which allows an attacker to potentially gain remote code execution or cause denial of service via the channel definition cdef atom of JPEG2000.

## References
- https://github.com/google/security-research/security/advisories/GHSA-39q3-f8jq-v6mg
