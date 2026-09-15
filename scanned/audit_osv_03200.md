# [M] ALPINE-CVE-2025-15468

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-15468
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-15468
Type: osv

## Affected
- Alpine:v3.20: `openssl` — affected >=3.3.0 <3.3.6-r0
- Alpine:v3.21: `openssl` — affected >=3.3.0 <3.3.6-r0
- Alpine:v3.22: `openssl` — affected >=3.3.0 <3.5.5-r0
- Alpine:v3.23: `openssl` — affected >=3.3.0 <3.5.5-r0
- Alpine:v3.24: `openssl` — affected >=3.3.0 <3.5.5-r0

## Details
Issue summary: If an application using the SSL_CIPHER_find() function in
a QUIC protocol client or server receives an unknown cipher suite from
the peer, a NULL dereference occurs.

Impact summary: A NULL pointer dereference leads to abnormal termination of
the running process causing Denial of Service.

Some applications call SSL_CIPHER_find() from the client_hello_cb callback
on the cipher ID received from the peer. If this is done with an SSL object
implementing the QUIC protocol, NULL pointer dereference will happen if
the examined cipher ID is unknown or unsupported.

As it is not very common to call this function in applications using the QUIC 
protocol and the worst outcome is Denial of Service, the issue was assessed
as Low severity.

The vulnerable code was introduced in the 3.2 version with the addition
of the QUIC protocol support.

The FIPS modules in 3.6, 3.5, 3.4 and 3.3 are not affected by this issue,
as the QUIC implementation is outside the OpenSSL FIPS module boundary.

OpenSSL 3.6, 3.5, 3.4 and 3.3 are vulnerable to this issue.

OpenSSL 3.0, 1.1.1 and 1.0.2 are not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-15468
