# [M] ALPINE-CVE-2025-0620

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-0620
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-06-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-0620
Type: osv

## Affected
- Alpine:v3.22: `samba` — affected >=4.21.0 <4.21.6-r0
- Alpine:v3.23: `samba` — affected >=4.21.0 <4.21.6-r0
- Alpine:v3.24: `samba` — affected >=4.21.0 <4.21.6-r0

## Details
A flaw was found in Samba. The smbd service daemon does not pick up group membership changes when re-authenticating an expired SMB session. This issue can expose file shares until clients disconnect and then connect again.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-0620
