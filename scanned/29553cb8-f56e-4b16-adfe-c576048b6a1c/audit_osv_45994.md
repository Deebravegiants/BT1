# [C] JLSEC-2026-552

## Summary
Severity: Critical
Advisory: JLSEC-2026-552
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-552
Type: osv

## Affected
- Julia: `OpenJpeg_jll` — affected >=0 <2.5.5+0

## Details
OpenJPEG is an open-source JPEG 2000 codec. In OpenJPEG from 2.5.1 through 2.5.3, a call to `opj_jp2_read_header` may lead to OOB heap memory write when the data stream `p_stream` is too short and `p_image` is not initialized.

## References
- https://github.com/uclouvain/openjpeg/commit/f809b80c67717c152a5ad30bf06774f00da4fd2d
- https://github.com/uclouvain/openjpeg/pull/1573
- https://securitylab.github.com/advisories/GHSL-2025-057_OpenCV
