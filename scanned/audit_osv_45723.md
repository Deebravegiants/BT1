# [M] Issue summary: If an application using the `SSL_CIPHER_find()` function in a QUIC protocol client or...

## Summary
Severity: Medium
Advisory: JLSEC-2026-257
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-257
Type: osv

## Affected
- Julia: `OpenSSL_jll` — affected >=3.5.0+0 <3.5.5+0

## Details
Issue summary: If an application using the `SSL_CIPHER_find()` function in
a QUIC protocol client or server receives an unknown cipher suite from
the peer, a NULL dereference occurs.

Impact summary: A NULL pointer dereference leads to abnormal termination of
the running process causing Denial of Service.

Some applications call `SSL_CIPHER_find()` from the `client_hello_cb` callback
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
- https://github.com/advisories/GHSA-rhx3-fg8p-f9m4
- https://github.com/openssl/openssl/commit/1f08e54bad32843044fe8a675948d65e3b4ece65
- https://github.com/openssl/openssl/commit/7c88376731c589ee5b36116c5a6e32d5ae5f7ae2
- https://github.com/openssl/openssl/commit/b2539639400288a4580fe2d76247541b976bade4
- https://github.com/openssl/openssl/commit/d75b309879631d45b972396ce4e5102559c64ac7
- https://nvd.nist.gov/vuln/detail/CVE-2025-15468
- https://openssl-library.org/news/secadv/20260127.txt
