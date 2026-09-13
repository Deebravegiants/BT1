# [H] ALPINE-CVE-2026-48711

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-48711
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-48711
Type: osv

## Affected
- Alpine:v3.20: `sshfs` — affected >=0 <3.7.6-r0
- Alpine:v3.21: `sshfs` — affected >=0 <3.7.6-r0
- Alpine:v3.22: `sshfs` — affected >=0 <3.7.6-r0
- Alpine:v3.23: `sshfs` — affected >=0 <3.7.6-r0
- Alpine:v3.24: `sshfs` — affected >=0 <3.7.6-r0

## Details
SSHFS is a network filesystem client for connecting to SSH servers. From version 1.4 until 3.7.6, SSHFS accepts a bracketed mount source such as [-oProxyCommand=CMD]:/path and find_base_path() removes the brackets, leaving a host value that begins with - and is passed directly to ssh as a command-line argument. When a caller also supplies a path-valued sftp_server, ssh treats the normalized host as an option and the server path as its destination, causing an injected ProxyCommand to execute locally before any connection or authentication succeeds. The attack requires a caller or wrapper that passes an attacker-controlled mount source to SSHFS with the required sftp_server configuration and results in arbitrary command execution as the user running SSHFS. This issue is fixed in version 3.7.6.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-48711
