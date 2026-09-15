# [C] MongoDB Improper Input Validation in Compute Mode External Data Processing Leading to Memory Corruption

## Summary
Severity: Critical
Advisory: BIT-mongodb-2026-13072
Aliases: CVE-2026-13072
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13072
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
When compute mode is enabled on a standalone mongod instance, insufficient validation of externally sourced BSON data during aggregation pipeline processing can result in memory corruption, potentially leading to process termination or other unintended behavior. This configuration is non-default and requires explicit enablement at startup.

## References
- https://jira.mongodb.org/browse/SERVER-128494
- https://nvd.nist.gov/vuln/detail/CVE-2026-13072
