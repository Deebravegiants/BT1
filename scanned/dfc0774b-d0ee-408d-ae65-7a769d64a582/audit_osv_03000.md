# [H] ALPINE-CVE-2024-23185

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-23185
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-09-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-23185
Type: osv

## Affected
- Alpine:v3.21: `dovecot` — affected >=0 <2.3.21.1-r0
- Alpine:v3.22: `dovecot` — affected >=0 <2.3.21.1-r0
- Alpine:v3.23: `dovecot` — affected >=0 <2.3.21.1-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.3.21.1-r0

## Details
Very large headers can cause resource exhaustion when parsing message. The message-parser normally reads reasonably sized chunks of the message. However, when it feeds them to message-header-parser, it starts building up "full_value" buffer out of the smaller chunks. The full_value buffer has no size limit, so large headers can cause large memory usage. It doesn't matter whether it's a single long header line, or a single header split into multiple lines. This bug exists in all Dovecot versions. Incoming mails typically have some size limits set by MTA, so even largest possible header size may still fit into Dovecot's vsz_limit. So attackers probably can't DoS a victim user this way. A user could APPEND larger mails though, allowing them to DoS themselves (although maybe cause some memory issues for the backend in general). One can implement restrictions on headers on MTA component preceding Dovecot. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-23185
