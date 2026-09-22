# [H] ALPINE-CVE-2026-53791

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-53791
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-53791
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync daemon before 3.5.0 contains an IP address spoofing vulnerability that allows unauthenticated remote attackers to bypass IP-based access controls by sending a crafted PROXY protocol header with a forged source address. Attackers who can connect directly to the rsync daemon can inject a spoofed source IP in the PROXY protocol header to circumvent hosts allow/deny rules, gaining unauthorized access that would otherwise be blocked based on their real source address.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-53791
