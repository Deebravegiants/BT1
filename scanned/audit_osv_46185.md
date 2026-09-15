# [C] JLSEC-2026-776

## Summary
Severity: Critical
Advisory: JLSEC-2026-776
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/JLSEC-2026-776
Type: osv

## Affected
- Julia: `HarfBuzz_ICU_jll` — affected >=8.5.0+0 <100.14002.1+0
- Julia: `HarfBuzz_jll` — affected >=8.5.0+0 <100.14002.1+0

## Details
HarfBuzz is a text shaping engine. Starting with 8.5.0 through 10.0.1, there is a heap-based buffer overflow in the `hb_cairo_glyphs_from_buffer` function.

## References
- https://github.com/harfbuzz/harfbuzz/commit/1767f99e2e2196c3fcae27db6d8b60098d3f6d26
- https://github.com/harfbuzz/harfbuzz/security/advisories/GHSA-qmp9-xqm5-jh6m
