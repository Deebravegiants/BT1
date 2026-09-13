# [M] RFC7250 handshakes with unauthenticated servers don't abort as expected

## Summary
Severity: Medium
Advisory: CVE-2024-12797
Aliases: GHSA-79v4-65xg-pq4g, PYSEC-2026-1284
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-02-11
Source: https://osv.dev/vulnerability/CVE-2024-12797
Type: osv

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
- http://www.openwall.com/lists/oss-security/2025/02/11/3
- http://www.openwall.com/lists/oss-security/2025/02/11/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12797.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12797
- https://openssl-library.org/news/secadv/20250211.txt
- https://security.netapp.com/advisory/ntap-20250214-0001/
- https://github.com/openssl/openssl/commit/738d4f9fdeaad57660dcba50a619fafced3fd5e9
- https://github.com/openssl/openssl/commit/798779d43494549b611233f92652f0da5328fbe7
- https://github.com/openssl/openssl/commit/87ebd203feffcf92ad5889df92f90bb0ee10a699
