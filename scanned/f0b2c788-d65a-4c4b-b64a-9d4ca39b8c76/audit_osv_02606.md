# [M] ALPINE-CVE-2022-3592

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-3592
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-01-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-3592
Type: osv

## Affected
- Alpine:v3.15: `samba` — affected >=4.17.0 <4.15.12-r0
- Alpine:v3.16: `samba` — affected >=4.17.0 <4.15.12-r0
- Alpine:v3.17: `samba` — affected >=4.17.0 <4.16.6-r0
- Alpine:v3.18: `samba` — affected >=4.17.0 <4.16.6-r0
- Alpine:v3.19: `samba` — affected >=4.17.0 <4.16.6-r0
- Alpine:v3.20: `samba` — affected >=4.17.0 <4.16.6-r0
- Alpine:v3.21: `samba` — affected >=4.17.0 <4.16.6-r0
- Alpine:v3.22: `samba` — affected >=4.17.0 <4.16.6-r0
- Alpine:v3.23: `samba` — affected >=4.17.0 <4.16.6-r0
- Alpine:v3.24: `samba` — affected >=4.17.0 <4.16.6-r0

## Details
A symlink following vulnerability was found in Samba, where a user can create a symbolic link that will make 'smbd' escape the configured share path. This flaw allows a remote user with access to the exported part of the file system under a share via SMB1 unix extensions or NFS to create symlinks to files outside the 'smbd' configured share path and gain access to another restricted server's filesystem.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-3592
