# [M] Partial-chain verification accepts untrusted intermediate as trust anchor

## Summary
Severity: Medium
Advisory: CVE-2026-6091
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-6091
Type: osv

## Details
Partial-chain certificate verification may accept chains that terminate at a peer-supplied, untrusted intermediate certificate rather than a trusted anchor. An attacker could present a chain that ends at an intermediate they control and have it accepted as valid. This affects the OpenSSL compatibility certificate-path-building path (wolfSSL_X509_verify_cert / X509_STORE, OPENSSL_EXTRA) when the X509_V_FLAG_PARTIAL_CHAIN verify flag is enabled.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6091.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6091
- https://github.com/wolfSSL/wolfssl/pull/10170
- https://github.com/wolfSSL/wolfssl
