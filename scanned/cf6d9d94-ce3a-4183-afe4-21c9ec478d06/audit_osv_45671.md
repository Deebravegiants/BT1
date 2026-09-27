# [H] JLSEC-2026-188

## Summary
Severity: High
Advisory: JLSEC-2026-188
Ecosystem: Julia
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-188
Type: osv

## Affected
- Julia: `assimp_jll` — affected >=0 <6.0.4+0

## Details
Heap-based buffer overflow vulnerability in Assimp versions prior to 5.4.3 allows a local attacker to execute arbitrary code by importing a specially crafted file into the product.

## References
- https://github.com/assimp/assimp/releases/tag/v5.4.3
- https://jvn.jp/en/jp/JVN42386607/
