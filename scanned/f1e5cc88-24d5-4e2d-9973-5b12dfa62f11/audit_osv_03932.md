# [M] ALPINE-CVE-2026-70455

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-70455
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-70455
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=3.4.2 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=3.4.2 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=3.4.2 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=3.4.2 <3.5.0-r0

## Details
rsync 3.4.2 before 3.5.0 contains a denial of service vulnerability that allows a remote sender to exhaust system resources by specifying the --zt short alias for --compress-threads, which bypasses the refuse options directive's string matching on long option names. Attackers can specify --zt=N with a large value to spawn an unbounded number of Zstandard worker threads on the receiver, exhausting available thread and memory resources.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-70455
