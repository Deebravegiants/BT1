# [H] ALPINE-CVE-2022-29154

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-29154
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-08-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-29154
Type: osv

## Affected
- Alpine:v3.13: `rsync` — affected >=0 <3.2.4-r0
- Alpine:v3.14: `rsync` — affected >=0 <3.2.4-r0
- Alpine:v3.15: `rsync` — affected >=0 <3.2.4-r0
- Alpine:v3.16: `rsync` — affected >=0 <3.2.4-r2
- Alpine:v3.17: `rsync` — affected >=0 <3.2.4-r2
- Alpine:v3.18: `rsync` — affected >=0 <3.2.4-r2
- Alpine:v3.19: `rsync` — affected >=0 <3.2.4-r2
- Alpine:v3.20: `rsync` — affected >=0 <3.2.4-r2
- Alpine:v3.21: `rsync` — affected >=0 <3.2.4-r2
- Alpine:v3.22: `rsync` — affected >=0 <3.2.4-r2
- Alpine:v3.23: `rsync` — affected >=0 <3.2.4-r2
- Alpine:v3.24: `rsync` — affected >=0 <3.2.4-r2

## Details
An issue was discovered in rsync before 3.2.5 that allows malicious remote servers to write arbitrary files inside the directories of connecting peers. The server chooses which files/directories are sent to the client. However, the rsync client performs insufficient validation of file names. A malicious rsync server (or Man-in-The-Middle attacker) can overwrite arbitrary files in the rsync client target directory and subdirectories (for example, overwrite the .ssh/authorized_keys file).

## References
- https://security.alpinelinux.org/vuln/CVE-2022-29154
