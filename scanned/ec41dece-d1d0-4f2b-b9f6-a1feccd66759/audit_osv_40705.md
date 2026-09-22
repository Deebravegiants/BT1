# [M] wolfSSL ARIA-GCM TLS 1.2/DTLS 1.2 GCM nonce reuse

## Summary
Severity: Medium
Advisory: CVE-2026-5446
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-5446
Type: osv

## Details
In wolfSSL, ARIA-GCM cipher suites used in TLS 1.2 and DTLS 1.2 reuse an identical 12-byte GCM nonce for every application-data record. Because wc_AriaEncrypt is stateless and passes the caller-supplied IV verbatim to the MagicCrypto SDK with no internal counter, and because the explicit IV is zero-initialized at session setup and never incremented in non-FIPS builds. This vulnerability affects wolfSSL builds configured with --enable-aria and the proprietary MagicCrypto SDK (a non-default, opt-in configuration required for Korean regulatory deployments). AES-GCM is not affected because wc_AesGcmEncrypt_ex maintains an internal invocation counter independently of the call-site guard.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5446.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5446
- https://github.com/wolfSSL/wolfssl/pull/10111
- https://github.com/wolfSSL/wolfssl
