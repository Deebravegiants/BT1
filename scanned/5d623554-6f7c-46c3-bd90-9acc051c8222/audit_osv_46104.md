# [M] An issue was discovered in wolfSSL before 5.7.0

## Summary
Severity: Medium
Advisory: JLSEC-2026-683
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-683
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
An issue was discovered in wolfSSL before 5.7.0. A safe-error attack via Rowhammer, namely FAULT+PROBE, leads to ECDSA key disclosure. When `WOLFSSL_CHECK_SIG_FAULTS` is used in signing operations with private ECC keys,

such as in server-side TLS connections, the connection is halted if any fault occurs. The success rate in a certain amount of connection requests can be processed via an advanced technique for ECDSA key recovery.

## References
- https://github.com/advisories/GHSA-rrg9-cmw9-3pwx
- https://github.com/wolfSSL/wolfssl/releases/tag/v5.7.2-stable
- https://nvd.nist.gov/vuln/detail/CVE-2024-5288
