# [C] Heap buffer overread in `wc_PKCS7_DecodeEnvelopedData` when parsing crafted PKCS7 EnvelopedData

## Summary
Severity: Critical
Advisory: JLSEC-2026-744
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-744
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.8.4+0 <5.9.2+0

## Details
Heap buffer overread in `wc_PKCS7_DecodeEnvelopedData` when parsing crafted PKCS7 EnvelopedData. This could theoretically be triggered by attacker-supplied data delivered via S/MIME or CMS.

## References
- https://github.com/advisories/GHSA-h6gc-rmv2-74g6
- https://github.com/wolfSSL/wolfssl/pull/10128
- https://nvd.nist.gov/vuln/detail/CVE-2026-6094
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
