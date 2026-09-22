# [M] ALPINE-CVE-2024-12086

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-12086
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-01-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-12086
Type: osv

## Affected
- Alpine:v3.18: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.19: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.20: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.21: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.4.0-r0

## Details
A flaw was found in rsync. It could allow a server to enumerate the contents of an arbitrary file from the client's machine. This issue occurs when files are being copied from a client to a server. During this process, the rsync server will send checksums of local data to the client to compare with in order to determine what data needs to be sent to the server. By sending specially constructed checksum values for arbitrary files, an attacker may be able to reconstruct the data of those files byte-by-byte based on the responses from the client.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-12086
