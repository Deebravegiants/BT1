# [H] BIT-java-2025-47219

## Summary
Severity: High
Advisory: BIT-java-2025-47219
Aliases: BIT-java-min-2025-47219, BIT-jre-2025-47219, CVE-2025-47219
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2025-47219
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.481

## Details
In GStreamer through 1.26.1, the isomp4 plugin's qtdemux_parse_trak function may read past the end of a heap buffer while parsing an MP4 file, possibly leading to information disclosure.

## References
- https://github.com/atredispartners/advisories/blob/master/2025/ATREDIS-2025-0003.md
- https://gstreamer.freedesktop.org/security/
- https://nvd.nist.gov/vuln/detail/CVE-2025-47219
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
