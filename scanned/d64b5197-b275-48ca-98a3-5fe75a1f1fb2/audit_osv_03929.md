# [H] ALPINE-CVE-2026-70452

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-70452
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-70452
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync 3.1.0 before 3.5.0 contains an access control bypass vulnerability that allows remote attackers to circumvent hosts deny rules by inducing DNS resolution failures during hostname-based access control evaluation. When a DNS lookup for a hostname-based deny rule fails, the daemon skips the rule rather than defaulting to a deny decision, enabling attackers who can trigger DNS failures to bypass module-level IP access controls and gain unauthorized access to restricted module file trees.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-70452
