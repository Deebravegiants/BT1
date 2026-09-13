# [M] TLS 1.3 CompressedCertificate excessive memory allocation

## Summary
Severity: Medium
Advisory: CVE-2025-66199
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2025-66199
Type: osv

## Details
Issue summary: A TLS 1.3 connection using certificate compression can be
forced to allocate a large buffer before decompression without checking
against the configured certificate size limit.

Impact summary: An attacker can cause per-connection memory allocations of
up to approximately 22 MiB and extra CPU work, potentially leading to
service degradation or resource exhaustion (Denial of Service).

In affected configurations, the peer-supplied uncompressed certificate
length from a CompressedCertificate message is used to grow a heap buffer
prior to decompression. This length is not bounded by the max_cert_list
setting, which otherwise constrains certificate message sizes. An attacker
can exploit this to cause large per-connection allocations followed by
handshake failure. No memory corruption or information disclosure occurs.

This issue only affects builds where TLS 1.3 certificate compression is
compiled in (i.e., not OPENSSL_NO_COMP_ALG) and at least one compression
algorithm (brotli, zlib, or zstd) is available, and where the compression
extension is negotiated. Both clients receiving a server CompressedCertificate
and servers in mutual TLS scenarios receiving a client CompressedCertificate
are affected. Servers that do not request client certificates are not
vulnerable to client-initiated attacks.

Users can mitigate this issue by setting SSL_OP_NO_RX_CERTIFICATE_COMPRESSION
to disable receiving compressed certificates.

The FIPS modules in 3.6, 3.5, 3.4 and 3.3 are not affected by this issue,
as the TLS implementation is outside the OpenSSL FIPS module boundary.

OpenSSL 3.6, 3.5, 3.4 and 3.3 are vulnerable to this issue.

OpenSSL 3.0, 1.1.1 and 1.0.2 are not affected by this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66199.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66199
- https://openssl-library.org/news/secadv/20260127.txt
- https://github.com/openssl/openssl/commit/3ed1f75249932b155eef993a8e66a99cb98bfef4
- https://github.com/openssl/openssl/commit/6184a4fb08ee6d7bca570d931a4e8bef40b64451
- https://github.com/openssl/openssl/commit/895150b5e021d16b52fb32b97e1dd12f20448be5
- https://github.com/openssl/openssl/commit/966a2478046c311ed7dae50c457d0db4cafbf7e4
