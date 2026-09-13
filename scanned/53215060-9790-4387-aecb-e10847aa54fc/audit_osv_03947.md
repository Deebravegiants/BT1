# [C] ALPINE-CVE-2026-73072

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-73072
Ecosystem: Alpine:v3.23
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-73072
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0846, set_sofo() in src/spellfile.c reuses sl_sal_first[] without resetting values left by set_sal_first(), so a crafted spell file containing an SN_SAL section before an SN_SOFO section causes under-counted mapping lists and attacker-influenced writes beyond a heap allocation. This issue is fixed in version 9.2.0846.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-73072
