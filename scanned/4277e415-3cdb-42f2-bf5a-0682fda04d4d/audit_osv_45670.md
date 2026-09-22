# [H] JLSEC-2026-187

## Summary
Severity: High
Advisory: JLSEC-2026-187
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-187
Type: osv

## Affected
- Julia: `assimp_jll` — affected >=0 <6.0.4+0

## Details
Heap-based buffer overflow vulnerability in Assimp versions prior to 5.4.2 allows a local attacker to execute arbitrary code by inputting a specially crafted file into the product.

## References
- https://github.com/assimp/assimp/pull/5651/commits/614911bb3b1bfc3a1799ae2b3cca306270f3fb97
- https://github.com/assimp/assimp/releases/tag/v5.4.2
- https://jvn.jp/en/jp/JVN87710540/
