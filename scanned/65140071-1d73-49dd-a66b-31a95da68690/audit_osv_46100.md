# [M] wolfSSL prior to 5.6.6 did not check that messages in one (D)TLS record do not span key boundaries

## Summary
Severity: Medium
Advisory: JLSEC-2026-679
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-679
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
wolfSSL prior to 5.6.6 did not check that messages in one (D)TLS record do not span key boundaries. As a result, it was possible to combine (D)TLS messages using different keys into one (D)TLS record. The most extreme edge case is that, in (D)TLS 1.3, it was possible that an unencrypted (D)TLS 1.3 record from the server containing first a ServerHello message and then the rest of the first server flight would be accepted by a wolfSSL client. In (D)TLS 1.3 the handshake is encrypted after the ServerHello but a wolfSSL client would accept an unencrypted flight from the server. This does not compromise key negotiation and authentication so it is assigned a low severity rating.

## References
- https://github.com/advisories/GHSA-ff3x-q8pg-rh37
- https://github.com/wolfSSL/wolfssl/pull/7029
- https://nvd.nist.gov/vuln/detail/CVE-2023-6937
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
