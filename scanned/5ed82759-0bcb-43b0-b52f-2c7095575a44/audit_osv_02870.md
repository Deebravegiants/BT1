# [M] ALPINE-CVE-2023-4091

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-4091
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-4091
Type: osv

## Affected
- Alpine:v3.18: `samba` — affected >=4.18.0 <4.18.8-r0
- Alpine:v3.19: `samba` — affected >=4.18.0 <4.18.8-r0
- Alpine:v3.20: `samba` — affected >=4.18.0 <4.18.8-r0
- Alpine:v3.21: `samba` — affected >=4.18.0 <4.18.8-r0
- Alpine:v3.22: `samba` — affected >=4.18.0 <4.18.8-r0
- Alpine:v3.23: `samba` — affected >=4.18.0 <4.18.8-r0
- Alpine:v3.24: `samba` — affected >=4.18.0 <4.18.8-r0

## Details
A vulnerability was discovered in Samba, where the flaw allows SMB clients to truncate files, even with read-only permissions when the Samba VFS module "acl_xattr" is configured with "acl_xattr:ignore system acls = yes". The SMB protocol allows opening files when the client requests read-only access but then implicitly truncates the opened file to 0 bytes if the client specifies a separate OVERWRITE create disposition request. The issue arises in configurations that bypass kernel file system permissions checks, relying solely on Samba's permissions.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-4091
