# [H] BIT-java-2023-25193

## Summary
Severity: High
Advisory: BIT-java-2023-25193
Aliases: BIT-java-min-2023-25193, BIT-jre-2023-25193, CVE-2023-25193
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2023-25193
Type: osv

## Affected
- Bitnami: `java` — affected >=18.0.0 <20.0.2

## Details
hb-ot-layout-gsubgpos.hh in HarfBuzz through 6.0.0 allows attackers to trigger O(n^2) growth via consecutive marks during the process of looking back for base glyphs when attaching marks.

## References
- https://chromium.googlesource.com/chromium/src/+/e1f324aa681af54101c1f2d173d92adb80e37088/DEPS#361
- https://github.com/harfbuzz/harfbuzz/blob/2822b589bc837fae6f66233e2cf2eef0f6ce8470/src/hb-ot-layout-gsubgpos.hh
- https://github.com/harfbuzz/harfbuzz/commit/85be877925ddbf34f74a1229f3ca1716bb6170dc
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KWCHWSICWVZSAXP2YAXM65JC2GR53547/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZ5M2GSAIHFPLHYJXUPQ2QDJCLWXUGO3/
- https://nvd.nist.gov/vuln/detail/CVE-2023-25193
- https://openjdk.org/groups/vulnerability/advisories/2023-07-18
- https://security.netapp.com/advisory/ntap-20230725-0006/
- https://www.oracle.com/security-alerts/cpujul2023.html
