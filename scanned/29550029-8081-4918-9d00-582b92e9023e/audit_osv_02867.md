# [C] ALPINE-CVE-2023-3961

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-3961
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-3961
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
A path traversal vulnerability was identified in Samba when processing client pipe names connecting to Unix domain sockets within a private directory. Samba typically uses this mechanism to connect SMB clients to remote procedure call (RPC) services like SAMR LSA or SPOOLSS, which Samba initiates on demand. However, due to inadequate sanitization of incoming client pipe names, allowing a client to send a pipe name containing Unix directory traversal characters (../). This could result in SMB clients connecting as root to Unix domain sockets outside the private directory. If an attacker or client managed to send a pipe name resolving to an external service using an existing Unix domain socket, it could potentially lead to unauthorized access to the service and consequential adverse events, including compromise or service crashes.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-3961
