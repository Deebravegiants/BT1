# [M] ALPINE-CVE-2019-6111

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-6111
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-01-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6111
Type: osv

## Affected
- Alpine:v3.24: `dropbear` — affected >=0 <2026.91-r0
- Alpine:v3.10: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.11: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.12: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.13: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.14: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.15: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.16: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.17: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.18: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.19: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.20: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.21: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.22: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.23: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.24: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.6: `openssh` — affected >=0 <7.5_p1-r4
- Alpine:v3.7: `openssh` — affected >=0 <7.5_p1-r10
- Alpine:v3.8: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.9: `openssh` — affected >=0 <7.9_p1-r3

## Details
An issue was discovered in OpenSSH 7.9. Due to the scp implementation being derived from 1983 rcp, the server chooses which files/directories are sent to the client. However, the scp client only performs cursory validation of the object name returned (only directory traversal attacks are prevented). A malicious scp server (or Man-in-The-Middle attacker) can overwrite arbitrary files in the scp client target directory. If recursive operation (-r) is performed, the server can manipulate subdirectories as well (for example, to overwrite the .ssh/authorized_keys file).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6111
