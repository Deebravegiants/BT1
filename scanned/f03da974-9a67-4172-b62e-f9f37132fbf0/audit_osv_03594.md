# [M] ALPINE-CVE-2026-33263

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-33263
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33263
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.5-r0

## Details
When mail_max_userip_connections is set (default 10) and reached, submission-login can crash with epoll() panic caused by file descriptor handling issues. If running in high-security mode (default for community releases), only the new submission connection gets terminated. If running in high-performance mode (default for Pro releases), all connections handled by the submission-login process will be terminated. The crashes can cause failure for user to send a message, or it can cause duplicate messages to be sent. If TLS is not used (in the backend server processing the submission), duplicate deliveries cannot happen, because the crash can only happen at AUTH stage. Limit the number of connections handled by single submission-login process. This has a performance impact though. Update to non-vulnerable version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33263
