# [M] A padding oracle exists in wolfSSL's PKCS7 CBC decryption that could allow an attacker to recover...

## Summary
Severity: Medium
Advisory: JLSEC-2026-732
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-732
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
A padding oracle exists in wolfSSL's PKCS7 CBC decryption that could allow an attacker to recover plaintext through repeated decryption queries with modified ciphertext. In previous versions of wolfSSL the interior padding bytes are not validated.

## References
- https://github.com/advisories/GHSA-qvjw-73xm-jw34
- https://github.com/wolfSSL/wolfssl/pull/10088
- https://nvd.nist.gov/vuln/detail/CVE-2026-5504
