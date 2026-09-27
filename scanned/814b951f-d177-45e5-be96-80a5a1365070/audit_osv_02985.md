# [M] ALPINE-CVE-2024-12797

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-12797
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-02-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-12797
Type: osv

## Affected
- Alpine:v3.20: `openssl` — affected >=0 <3.3.3-r0
- Alpine:v3.21: `openssl` — affected >=0 <3.3.3-r0
- Alpine:v3.22: `openssl` — affected >=0 <3.3.3-r0
- Alpine:v3.23: `openssl` — affected >=0 <3.3.3-r0
- Alpine:v3.24: `openssl` — affected >=0 <3.3.3-r0

## Details
Issue summary: Clients using RFC7250 Raw Public Keys (RPKs) to authenticate a
server may fail to notice that the server was not authenticated, because
handshakes don't abort as expected when the SSL_VERIFY_PEER verification mode
is set.

Impact summary: TLS and DTLS connections using raw public keys may be
vulnerable to man-in-middle attacks when server authentication failure is not
detected by clients.

RPKs are disabled by default in both TLS clients and TLS servers.  The issue
only arises when TLS clients explicitly enable RPK use by the server, and the
server, likewise, enables sending of an RPK instead of an X.509 certificate
chain.  The affected clients are those that then rely on the handshake to
fail when the server's RPK fails to match one of the expected public keys,
by setting the verification mode to SSL_VERIFY_PEER.

Clients that enable server-side raw public keys can still find out that raw
public key verification failed by calling SSL_get_verify_result(), and those
that do, and take appropriate action, are not affected.  This issue was
introduced in the initial implementation of RPK support in OpenSSL 3.2.

The FIPS modules in 3.4, 3.3, 3.2, 3.1 and 3.0 are not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-12797
