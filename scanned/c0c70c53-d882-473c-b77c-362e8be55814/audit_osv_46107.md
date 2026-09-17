# [H] Integer Underflow Leads to Out-of-Bounds Access in XChaCha20-Poly1305 Decrypt

## Summary
Severity: High
Advisory: JLSEC-2026-686
Ecosystem: Julia
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-686
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.8.4+0 <5.9.2+0

## Details
Integer Underflow Leads to Out-of-Bounds Access in XChaCha20-Poly1305 Decrypt. This issue is hit specifically with a call to the function `wc_XChaCha20Poly1305_Decrypt()` which is not used with TLS connections, only from direct calls from an application.

## References
- https://github.com/advisories/GHSA-h957-386q-gm5j
- https://github.com/wolfSSL/wolfssl/pull/9223
- https://nvd.nist.gov/vuln/detail/CVE-2025-11931
