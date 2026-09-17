# [M] X.509 trust-chain bypass via path-depth exhaustion in wolfSSL_X509_verify_cert()

## Summary
Severity: Medium
Advisory: CVE-2026-11999
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-11999
Type: osv

## Details
X.509 trust-chain bypass (path-depth exhaustion) in the OpenSSL compatibility certificate verifier (wolfSSL_X509_verify_cert()). This affects only builds with --enable-opensslextra whose application calls X509_verify_cert() with caller-supplied untrusted intermediates; for those users it is critical, otherwise the library is unaffected. Native wolfSSL TLS/DTLS usage is not impacted. X509_verify_cert() returned success based only on the last verified link rather than on reaching a trust anchor: when the supplied chain is deeper than the verifier's maximum path depth (default 100), path building runs out of depth while still walking untrusted intermediates and the chain is accepted even though it never reaches a configured trust anchor, allowing acceptance of an attacker-controlled certificate. The default TLS handshake (WOLFSSL_VERIFY_PEER) is not affected; only applications doing manual or deferred verification through this API are.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11999.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11999
- https://github.com/wolfSSL/wolfssl/pull/10674
- https://github.com/wolfSSL/wolfssl
