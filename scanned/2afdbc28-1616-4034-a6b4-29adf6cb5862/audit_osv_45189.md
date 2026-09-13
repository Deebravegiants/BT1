# [H] hb-ot-layout-gsubgpos.hh in HarfBuzz through 6.0.0 allows attackers to trigger O(n^2) growth via...

## Summary
Severity: High
Advisory: JLSEC-2025-175
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-21
Source: https://osv.dev/vulnerability/JLSEC-2025-175
Type: osv

## Affected
- Julia: `HarfBuzz_ICU_jll` — affected >=0 <8.5.0+0
- Julia: `HarfBuzz_jll` — affected >=0 <8.3.1+0

## Details
hb-ot-layout-gsubgpos.hh in HarfBuzz through 6.0.0 allows attackers to trigger O(n^2) growth via consecutive marks during the process of looking back for base glyphs when attaching marks.

## References
- https://chromium.googlesource.com/chromium/src/+/e1f324aa681af54101c1f2d173d92adb80e37088/DEPS#361
- https://github.com/harfbuzz/harfbuzz/blob/2822b589bc837fae6f66233e2cf2eef0f6ce8470/src/hb-ot-layout-gsubgpos.hh
- https://github.com/harfbuzz/harfbuzz/commit/85be877925ddbf34f74a1229f3ca1716bb6170dc
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KWCHWSICWVZSAXP2YAXM65JC2GR53547/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZ5M2GSAIHFPLHYJXUPQ2QDJCLWXUGO3/
- https://security.netapp.com/advisory/ntap-20230725-0006/
