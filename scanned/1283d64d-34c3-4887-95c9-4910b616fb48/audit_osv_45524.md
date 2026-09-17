# [H] JLSEC-2026-1272

## Summary
Severity: High
Advisory: JLSEC-2026-1272
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1272
Type: osv

## Affected
- Julia: `cryptopp_jll` — affected unspecified

## Details
gf2n.cpp in Crypto++ (aka cryptopp) through 8.9.0 allows attackers to cause a denial of service (application crash) via DER public-key data for an F(2^m) curve, if the degree of each term in the polynomial is not strictly decreasing.

## References
- https://github.com/weidai11/cryptopp/issues/1248
- https://github.com/weidai11/cryptopp/issues/1248
