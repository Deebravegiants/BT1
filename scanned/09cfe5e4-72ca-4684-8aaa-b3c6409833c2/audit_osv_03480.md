# [M] ALPINE-CVE-2026-1933

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-1933
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-1933
Type: osv

## Affected
- Alpine:v3.23: `samba` — affected >=4.1.0 <4.22.10-r0
- Alpine:v3.24: `samba` — affected >=4.1.0 <4.23.8-r0

## Details
A flaw was found in Samba’s handling of NTFS-style reparse points on shares configured with read only = yes. Due to missing SMB-layer access checks, authenticated users with underlying filesystem write permissions may create or delete reparse point metadata through SMB operations even on read-only exports. This could allow modification of SMB-visible file behavior, including converting files into symbolic links or other reparse point types.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-1933
