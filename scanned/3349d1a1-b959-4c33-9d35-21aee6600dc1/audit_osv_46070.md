# [H] When decoding an OpenEXR file that uses DWAA or DWAB compression, the specified raw length of...

## Summary
Severity: High
Advisory: JLSEC-2026-644
Ecosystem: Julia
CVSS: 7.5 (CVSS:4.0/AV:A/AC:H/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/JLSEC-2026-644
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=7.1.1+0 <8.0.0+0
- Julia: `FFplay_jll` — affected >=7.1.1+0 <8.1.2+0

## Details
When decoding an OpenEXR file that uses DWAA or DWAB compression, the specified raw length of run-length-encoded data is not checked when using it to calculate the output data.

We read `rle_raw_size` from the input file at [0], we decompress and decode into the buffer `td->rle_raw_data` of size `rle_raw_size` at [1], and then at [2] we will access entries in this buffer up to `(td->xsize - 1) * (td->ysize - 1) + rle_raw_size / 2`, which may exceed `rle_raw_size`.

We recommend upgrading to version 8.0 or beyond.

## References
- https://b.corp.google.com/issues/436510153
- https://github.com/advisories/GHSA-p7r5-qh99-qchm
- https://issuetracker.google.com/436510153
- https://nvd.nist.gov/vuln/detail/CVE-2025-59731
