# [H] The X25519 `x86_64` assembly implementation fails to clear the most significant bit during the final...

## Summary
Severity: High
Advisory: JLSEC-2026-695
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-695
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.7.2+0 <5.9.2+0

## Details
The X25519 `x86_64` assembly implementation fails to clear the most significant bit during the final modular reduction, so the computed result may not be fully reduced modulo the field prime 2^255 - 19. This can leave the field element in a non-canonical form, producing an incorrect result from the scalar multiplication and potentially a wrong shared secret. The final carry-propagation chains in the x64 and AVX2 reduction routines could overflow into the top bit, and the high limb was not masked afterward, so the 255-bit field element was left non-canonical.

## References
- https://github.com/advisories/GHSA-gjm7-vch5-hch8
- https://github.com/wolfSSL/wolfssl/pull/10536
- https://nvd.nist.gov/vuln/detail/CVE-2026-10512
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
