# [M] ALPINE-CVE-2020-28935

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-28935
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-28935
Type: osv

## Affected
- Alpine:v3.12: `nsd` — affected >=0 <4.3.4-r0
- Alpine:v3.13: `nsd` — affected >=0 <4.3.4-r0
- Alpine:v3.14: `nsd` — affected >=0 <4.3.4-r0
- Alpine:v3.15: `nsd` — affected >=0 <4.3.4-r0
- Alpine:v3.16: `nsd` — affected >=0 <4.3.4-r0
- Alpine:v3.17: `nsd` — affected >=0 <4.3.4-r0
- Alpine:v3.18: `nsd` — affected >=0 <4.3.4-r0
- Alpine:v3.19: `nsd` — affected >=0 <4.3.4-r0
- Alpine:v3.20: `nsd` — affected >=0 <4.3.4-r0
- Alpine:v3.21: `nsd` — affected >=0 <4.3.4-r0
- Alpine:v3.22: `nsd` — affected >=0 <4.3.4-r0
- Alpine:v3.23: `nsd` — affected >=0 <4.3.4-r0
- Alpine:v3.24: `nsd` — affected >=0 <4.3.4-r0

## Details
NLnet Labs Unbound, up to and including version 1.12.0, and NLnet Labs NSD, up to and including version 4.3.3, contain a local vulnerability that would allow for a local symlink attack. When writing the PID file, Unbound and NSD create the file if it is not there, or open an existing file for writing. In case the file was already present, they would follow symlinks if the file happened to be a symlink instead of a regular file. An additional chown of the file would then take place after it was written, making the user Unbound/NSD is supposed to run as the new owner of the file. If an attacker has local access to the user Unbound/NSD runs as, she could create a symlink in place of the PID file pointing to a file that she would like to erase. If then Unbound/NSD is killed and the PID file is not cleared, upon restarting with root privileges, Unbound/NSD will rewrite any file pointed at by the symlink. This is a local vulnerability that could create a Denial of Service of the system Unbound/NSD is running on. It requires an attacker having access to the limited permission user Unbound/NSD runs as and point through the symlink to a critical file on the system.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-28935
