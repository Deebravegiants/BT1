# [M] ALPINE-CVE-2026-70464

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-70464
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-70464
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync daemon 2.0.0 before 3.5.0 contains a denial of service vulnerability that allows unauthenticated remote attackers to exhaust daemon connection slots by stalling the handshake process before or after module selection without triggering the I/O timeout. Attackers can open many simultaneous connections and trickle data at the minimum rate to avoid timeout, or stall entirely before module selection where no timeout applies, consuming all available connection slots and denying service to legitimate clients.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-70464
