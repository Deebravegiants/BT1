# [H] When decoding an OpenEXR file that uses DWAA or DWAB compression, there's an implicit assumption...

## Summary
Severity: High
Advisory: JLSEC-2026-645
Ecosystem: Julia
CVSS: 7.5 (CVSS:4.0/AV:A/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/JLSEC-2026-645
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=7.1.1+0 <8.0.0+0
- Julia: `FFplay_jll` — affected >=7.1.1+0 <8.1.2+0

## Details
When decoding an OpenEXR file that uses DWAA or DWAB compression, there's an implicit assumption that the height and width are divisible by 8.

If the height or width of the image is not divisible by 8, the copy loops at [0] and [1] will continue to write until the next multiple of 8.

The buffer `td->uncompressed_data` is allocated in `decode_block` based on the precise height and width of the image, so the "rounded-up" multiple of 8 in the copy loop can exceed the buffer bounds, and the write block starting at [2] can corrupt following heap memory.

We recommend upgrading to version 8.0 or beyond.

## References
- https://b.corp.google.com/issues/436510316
- https://github.com/advisories/GHSA-qr3p-83wm-px3f
- https://issuetracker.google.com/436510316
- https://nvd.nist.gov/vuln/detail/CVE-2025-59732
