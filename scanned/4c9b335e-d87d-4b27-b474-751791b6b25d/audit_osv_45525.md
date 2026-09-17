# [H] JLSEC-2026-1273

## Summary
Severity: High
Advisory: JLSEC-2026-1273
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1273
Type: osv

## Affected
- Julia: `cryptopp_jll` — affected unspecified

## Details
ModularSquareRoot in Crypto++ (aka cryptopp) through 8.9.0 allows attackers to cause a denial of service (infinite loop) via crafted DER public-key data associated with squared odd numbers, such as the square of 268995137513890432434389773128616504853.

## References
- https://github.com/weidai11/cryptopp/issues/1249
- https://github.com/weidai11/cryptopp/issues/1249
