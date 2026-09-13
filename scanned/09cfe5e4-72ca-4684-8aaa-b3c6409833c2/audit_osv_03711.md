# [H] ALPINE-CVE-2026-42764

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-42764
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42764
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=3.5.0 <3.5.7-r0
- Alpine:v3.23: `openssl` — affected >=3.5.0 <3.5.7-r0
- Alpine:v3.24: `openssl` — affected >=3.5.0 <3.5.7-r0

## Details
Issue summary: Receiving a QUIC initial packet with an invalid token may
trigger a NULL pointer dereference in the OpenSSL QUIC server with
address validation disabled.

Impact summary: NULL pointer dereference typically causes abnormal termination
of the affected QUIC server process and a Denial of Service.

If the address validation is disabled in the OpenSSL QUIC server
implementation, an attacker can crash the server by sending an initial
packet with an invalid or expired token.

By default, the client address validation is enabled in the OpenSSL QUIC server
implementation, which makes the default configuration not vulnerable
to this issue. However if the SSL_LISTENER_FLAG_NO_VALIDATE is used with
the SSL_new_listener() call, the address validation is disabled making the
vulnerable code reachable.

The FIPS modules in 4.0, 3.6, 3.5, 3.4, and 3.0 are not affected by this
issue, as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42764
