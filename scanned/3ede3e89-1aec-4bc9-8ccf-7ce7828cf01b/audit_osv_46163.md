# [M] The ML-KEM ARM64 NEON ciphertext comparison only compares half of the input, breaking the...

## Summary
Severity: Medium
Advisory: JLSEC-2026-748
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-748
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.8.4+0 <5.9.2+0

## Details
The ML-KEM ARM64 NEON ciphertext comparison only compares half of the input, breaking the Fujisaki-Okamoto transform's implicit rejection and weakening IND-CCA2 security on that code path. The constant-time comparison effectively ignored part of the re-encrypted ciphertext, so a decapsulating party could fail to detect a manipulated ciphertext and proceed without the standard's required implicit rejection.

## References
- https://github.com/advisories/GHSA-89v8-3927-wfcg
- https://github.com/wolfSSL/wolfssl/pull/10192
- https://nvd.nist.gov/vuln/detail/CVE-2026-6330
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
