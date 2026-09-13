# [M] With TLS 1.2 connections a client can use any digest, specifically a weaker digest that is...

## Summary
Severity: Medium
Advisory: JLSEC-2026-687
Ecosystem: Julia
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-687
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.8.4+0 <5.9.2+0

## Details
With TLS 1.2 connections a client can use any digest, specifically a weaker digest that is supported, rather than those in the CertificateRequest.

## References
- https://github.com/advisories/GHSA-6wfx-6f8c-8wg4
- https://github.com/wolfSSL/wolfssl/pull/9395
- https://nvd.nist.gov/vuln/detail/CVE-2025-12889
