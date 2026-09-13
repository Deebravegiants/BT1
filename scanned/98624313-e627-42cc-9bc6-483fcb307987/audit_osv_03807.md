# [M] ALPINE-CVE-2026-52687

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-52687
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-52687
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.5-r0

## Details
An attacker that has valid credentials can select a compression algorithm for the IMAP connection whose decompression state requires a large amount of memory, and open several such connections. The memory limit of the process is reached with only a few connections, terminating the process and all connections it handles, which can cause degradation or denial of service for IMAP. Disable IMAP compression. Alternatively limit the number of connections handled by a single imap-login process, though this has a performance impact. Update to non-vulnerable version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-52687
