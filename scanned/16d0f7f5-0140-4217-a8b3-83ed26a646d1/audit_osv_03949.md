# [C] ALPINE-CVE-2026-73074

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-73074
Ecosystem: Alpine:v3.23
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-73074
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0841, prop_add_one() in src/textprop.c uses the proplen value from get_text_props() to increment a uint16_t property count beyond 0xffff, wrapping the count to zero and copying existing text-property records into a heap allocation sized for none of them. This issue is fixed in version 9.2.0841.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-73074
