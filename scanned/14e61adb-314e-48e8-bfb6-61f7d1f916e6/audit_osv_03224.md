# [C] ALPINE-CVE-2025-23395

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-23395
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-05-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-23395
Type: osv

## Affected
- Alpine:v3.21: `screen` — affected >=0 <5.0.1-r0
- Alpine:v3.22: `screen` — affected >=0 <5.0.1-r0
- Alpine:v3.23: `screen` — affected >=0 <5.0.1-r0
- Alpine:v3.24: `screen` — affected >=0 <5.0.1-r0

## Details
Screen 5.0.0 when it runs with setuid-root privileges does not drop privileges while operating on a user supplied path. This allows unprivileged users to create files in arbitrary locations with `root` ownership, the invoking user's (real) group ownership and file mode 0644. All data written to the Screen PTY will be logged into this file, allowing to escalate to root privileges

## References
- https://security.alpinelinux.org/vuln/CVE-2025-23395
