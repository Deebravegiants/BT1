# [C] ALPINE-CVE-2026-53790

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-53790
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-53790
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync before 3.5.0 contains multiple command and argument injection vulnerabilities that allow attackers to execute arbitrary commands by supplying malicious input through several code paths, including the RSYNC_CONNECT_PROG environment variable, daemon hooks, the rsync-ssl wrapper, and remote-shell command newline injection. Attackers can inject shell metacharacters or newline characters into unsanitized user-supplied values such as hostnames and hostspecs to execute arbitrary commands under the privileges of the rsync process or the invoking user.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-53790
