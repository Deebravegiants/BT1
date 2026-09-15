# [H] ALPINE-CVE-2026-27857

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-27857
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-27857
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=3.0.0 <2.4.3-r0
- Alpine:v3.24: `dovecot` — affected >=3.0.0 <2.4.3-r0

## Details
Sending "NOOP (((...)))" command with 4000 parenthesis open+close results in ~1MB extra memory usage. Longer commands will result in client disconnection. This 1 MB can be left allocated for longer time periods by not sending the command ending LF. So attacker could connect possibly from even a single IP and create 1000 connections to allocate 1 GB of memory, which would likely result in reaching VSZ limit and killing the process and its other proxied connections. Attacker could connect possibly from even a single IP and create 1000 connections to allocate 1 GB of memory, which would likely result in reaching VSZ limit and killing the process and its other proxied connections. Install fixed version, there is no other remediation. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-27857
