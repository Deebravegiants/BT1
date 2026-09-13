# [M] Partial-chain certificate verification may accept chains that terminate at a peer-supplied,...

## Summary
Severity: Medium
Advisory: JLSEC-2026-742
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-742
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.8.4+0 <5.9.2+0

## Details
Partial-chain certificate verification may accept chains that terminate at a peer-supplied, untrusted intermediate certificate rather than a trusted anchor. An attacker could present a chain that ends at an intermediate they control and have it accepted as valid. This affects the OpenSSL compatibility certificate-path-building path (`wolfSSL_X509_verify_cert` / `X509_STORE`, `OPENSSL_EXTRA`) when the `X509_V_FLAG_PARTIAL_CHAIN` verify flag is enabled.

## References
- https://github.com/advisories/GHSA-mhq8-94h7-mrgx
- https://github.com/wolfSSL/wolfssl/pull/10170
- https://nvd.nist.gov/vuln/detail/CVE-2026-6091
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
