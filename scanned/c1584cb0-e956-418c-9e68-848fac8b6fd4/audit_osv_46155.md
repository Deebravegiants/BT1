# [H] AES-GCM encryption/decryption with extremely large cumulative single message sizes (>64 GiB) were...

## Summary
Severity: High
Advisory: JLSEC-2026-739
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-739
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
AES-GCM encryption/decryption with extremely large cumulative single message sizes (>64 GiB) were not properly rejected by the streaming APIs, allowing counter wrap, keystream reuse, and consequent plaintext recovery.

## References
- https://github.com/advisories/GHSA-q4q5-jx42-4xp9
- https://github.com/wolfSSL/wolfssl/pull/10709
- https://nvd.nist.gov/vuln/detail/CVE-2026-55967
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
