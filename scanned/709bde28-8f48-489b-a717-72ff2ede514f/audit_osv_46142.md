# [M] X.509 date buffer overflow in `wolfSSL_X509_notAfter` / `wolfSSL_X509_notBefore`

## Summary
Severity: Medium
Advisory: JLSEC-2026-724
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-724
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
X.509 date buffer overflow in `wolfSSL_X509_notAfter` / `wolfSSL_X509_notBefore`. A buffer overflow may occur when parsing date fields from a crafted X.509 certificate via the compatibility layer API. This is only triggered when calling these two APIs directly from an application, and does not affect TLS or certificate verify operations in wolfSSL.

## References
- https://github.com/advisories/GHSA-5jqq-xpcr-q3r7
- https://github.com/wolfSSL/wolfssl/pull/10071
- https://nvd.nist.gov/vuln/detail/CVE-2026-5448
