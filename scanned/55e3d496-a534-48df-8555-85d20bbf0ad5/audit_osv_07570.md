# [M] Apache Superset: Lack of rate limiting allows for possible denial of service

## Summary
Severity: Medium
Advisory: BIT-superset-2023-42504
Aliases: CVE-2023-42504, GHSA-3hp7-4qq4-v5c6, PYSEC-2026-1157
Ecosystem: Bitnami
Published: 2025-02-05
Source: https://osv.dev/vulnerability/BIT-superset-2023-42504
Type: osv

## Affected
- Bitnami: `superset` — affected >=0 <3.0.0

## Details
An authenticated malicious user could initiate multiple concurrent requests, each requesting multiple dashboard exports, leading to a possible denial of service.

This issue affects Apache Superset: before 3.0.0

## References
- http://www.openwall.com/lists/oss-security/2023/11/28/6
- https://lists.apache.org/thread/yzq5gk1y9lyw6nxwd3xdkxg1djqw1h6l
- https://nvd.nist.gov/vuln/detail/CVE-2023-42504
