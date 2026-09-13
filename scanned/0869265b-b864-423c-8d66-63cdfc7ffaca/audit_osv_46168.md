# [M] Integer underflow in `wc_PKCS7_DecryptOri` when handling crafted Other Recipient Info, leading to...

## Summary
Severity: Medium
Advisory: JLSEC-2026-752
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-752
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
Integer underflow in `wc_PKCS7_DecryptOri` when handling crafted Other Recipient Info, leading to incorrect length handling during decryption.

## References
- https://github.com/advisories/GHSA-p894-8wv9-373j
- https://github.com/wolfSSL/wolfssl/pull/10203
- https://nvd.nist.gov/vuln/detail/CVE-2026-6678
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2408
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
