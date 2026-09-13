# [C] Dual-Algorithm CertificateVerify out-of-bounds read

## Summary
Severity: Critical
Advisory: JLSEC-2026-721
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-721
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
Dual-Algorithm CertificateVerify out-of-bounds read. When processing a dual-algorithm CertificateVerify message, an out-of-bounds read can occur on crafted input. This can only occur when --enable-experimental and --enable-dual-alg-certs is used when building wolfSSL.

## References
- https://github.com/advisories/GHSA-f4w6-5m9p-28hw
- https://github.com/wolfSSL/wolfssl/pull/10079
- https://nvd.nist.gov/vuln/detail/CVE-2026-5393
