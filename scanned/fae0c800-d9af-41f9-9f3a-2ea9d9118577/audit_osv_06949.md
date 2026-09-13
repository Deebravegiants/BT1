# [H] Using MaxKey() may crash the server

## Summary
Severity: High
Advisory: BIT-mongodb-2026-9749
Aliases: CVE-2026-9749
Ecosystem: Bitnami
Published: 2026-06-22
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-9749
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.3

## Details
This issue can occur when running an aggregation pipeline that uses the internal $exchange stage configured with key-range partitioning and order-preserving delivery. If a single key range produces enough documents to fill its exchange buffer (that is, many results are routed to the same consumer), the server reaches the code path where a full per-consumer buffer is detected but the internal "high watermark" for that key range is not updated as intended.

## References
- https://jira.mongodb.org/browse/SERVER-124031
- https://nvd.nist.gov/vuln/detail/CVE-2026-9749
