# [M] Timing side-channel in SM2 algorithm on 64 bit ARM

## Summary
Severity: Medium
Advisory: CVE-2025-9231
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-09-30
Source: https://osv.dev/vulnerability/CVE-2025-9231
Type: osv

## Details
Issue summary: A timing side-channel which could potentially allow remote
recovery of the private key exists in the SM2 algorithm implementation on 64 bit
ARM platforms.

Impact summary: A timing side-channel in SM2 signature computations on 64 bit
ARM platforms could allow recovering the private key by an attacker..

While remote key recovery over a network was not attempted by the reporter,
timing measurements revealed a timing signal which may allow such an attack.

OpenSSL does not directly support certificates with SM2 keys in TLS, and so
this CVE is not relevant in most TLS contexts.  However, given that it is
possible to add support for such certificates via a custom provider, coupled
with the fact that in such a custom provider context the private key may be
recoverable via remote timing measurements, we consider this to be a Moderate
severity issue.

The FIPS modules in 3.5, 3.4, 3.3, 3.2, 3.1 and 3.0 are not affected by this
issue, as SM2 is not an approved algorithm.

## References
- http://www.openwall.com/lists/oss-security/2025/09/30/5
- http://www.openwall.com/lists/oss-security/2026/05/11/11
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-089022.html
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://cert-portal.siemens.com/productcert/html/ssa-585531.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/9xxx/CVE-2025-9231.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-9231
- https://openssl-library.org/news/secadv/20250930.txt
- https://github.com/openssl/openssl/commit/567f64386e43683888212226824b6a179885a0fe
- https://github.com/openssl/openssl/commit/cba616c26ac8e7b37de5e77762e505ba5ca51698
- https://github.com/openssl/openssl/commit/eed5adc9f969d77c94f213767acbb41ff923b6f4
- https://github.com/openssl/openssl/commit/fc47a2ec078912b3e914fab5734535e76c4820c2
