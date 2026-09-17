# [M] ALPINE-CVE-2025-9640

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-9640
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-9640
Type: osv

## Affected
- Alpine:v3.22: `samba` — affected >=0 <4.21.9-r0
- Alpine:v3.23: `samba` — affected >=0 <4.21.9-r0
- Alpine:v3.24: `samba` — affected >=0 <4.21.9-r0

## Details
A flaw was found in Samba, in the vfs_streams_xattr module, where uninitialized heap memory could be written into alternate data streams. This allows an authenticated user to read residual memory content that may include sensitive data, resulting in an information disclosure vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-9640
