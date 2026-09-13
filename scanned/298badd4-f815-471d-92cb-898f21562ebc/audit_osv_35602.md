# [M] X.509 trust-chain bypass in wolfSSL_X509_verify_cert() via untrusted intermediate anchoring

## Summary
Severity: Medium
Advisory: CVE-2026-11310
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-11310
Type: osv

## Details
X.509 trust-chain bypass in the OpenSSL compatibility certificate verifier (wolfSSL_X509_verify_cert()). This affects only builds with --enable-opensslextra (OPENSSL_EXTRA) and whose application validates certificates by calling X509_verify_cert() with caller-supplied untrusted intermediate certificates; for those users it is critical, otherwise the library is unaffected. In particular, native wolfSSL TLS/DTLS usage is not impacted. wolfSSL's X509_verify_cert() temporarily loads each caller-supplied untrusted intermediate into the certificate manager but failed to drop them before the trusted-store check, so an untrusted intermediate could anchor the path itself. An attacker can present a chain that never reaches a configured trust anchor and have it accepted, resulting in acceptance of an attacker-controlled certificate. This is certificate verification independent of TLS (e.g. S/MIME/CMS, code/firmware signing, JWT/JWS x5c), is not specific to any key type or algorithm, and a single untrusted intermediate suffices. The default wolfSSL TLS handshake (WOLFSSL_VERIFY_PEER) is not affected; only TLS applications doing manual or deferred peer verification through this API are, which also requires --enable-sessioncerts.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11310.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11310
- https://github.com/wolfSSL/wolfssl/pull/10674
- https://github.com/wolfSSL/wolfssl
