# [M] Timing side-channel in ECDSA signature computation

## Summary
Severity: Medium
Advisory: CVE-2024-13176
CVSS: 4.1 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-01-20
Source: https://osv.dev/vulnerability/CVE-2024-13176
Type: osv

## Details
Issue summary: A timing side-channel which could potentially allow recovering
the private key exists in the ECDSA signature computation.

Impact summary: A timing side-channel in ECDSA signature computations
could allow recovering the private key by an attacker. However, measuring
the timing would require either local access to the signing application or
a very fast network connection with low latency.

There is a timing signal of around 300 nanoseconds when the top word of
the inverted ECDSA nonce value is zero. This can happen with significant
probability only for some of the supported elliptic curves. In particular
the NIST P-521 curve is affected. To be able to measure this leak, the attacker
process must either be located in the same physical computer or must
have a very fast network connection with low latency. For that reason
the severity of this vulnerability is Low.

The FIPS modules in 3.4, 3.3, 3.2, 3.1 and 3.0 are affected by this issue.

## References
- http://www.openwall.com/lists/oss-security/2025/01/20/2
- https://lists.debian.org/debian-lts-announce/2025/05/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/13xxx/CVE-2024-13176.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-13176
- https://openssl-library.org/news/secadv/20250120.txt
- https://security.netapp.com/advisory/ntap-20250124-0005/
- https://security.netapp.com/advisory/ntap-20250418-0010/
- https://security.netapp.com/advisory/ntap-20250502-0006/
- https://github.com/openssl/openssl/commit/07272b05b04836a762b4baa874958af51d513844
- https://github.com/openssl/openssl/commit/2af62e74fb59bc469506bc37eb2990ea408d9467
- https://github.com/openssl/openssl/commit/392dcb336405a0c94486aa6655057f59fd3a0902
- https://github.com/openssl/openssl/commit/4b1cb94a734a7d4ec363ac0a215a25c181e11f65
- https://github.com/openssl/openssl/commit/77c608f4c8857e63e98e66444e2e761c9627916f
- https://github.openssl.org/openssl/extended-releases/commit/0d5fd1ab987f7571e2c955d8d8b638fc0fb54ded
- https://github.openssl.org/openssl/extended-releases/commit/a2639000db19878d5d89586ae7b725080592ae86
