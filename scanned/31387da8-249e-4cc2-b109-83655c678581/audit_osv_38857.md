# [H] NULL Pointer Dereference in QUIC Server Initial Packet Handling

## Summary
Severity: High
Advisory: CVE-2026-42764
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-42764
Type: osv

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
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42764.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42764
- https://openssl-library.org/news/secadv/20260609.txt
- https://github.com/openssl/openssl/commit/5e3ed291b8af0b03d5d3b9e56a1da69a187e9729
- https://github.com/openssl/openssl/commit/a45a0aba8095682c88ff4fc4a784892b8c6f0677
- https://github.com/openssl/openssl/commit/bf29a458c1a231eca87e384c62b9c2553fa57a91
