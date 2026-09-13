# [M] Apache Superset: Sensitive Data Exposure via REST API (disabled by default)

## Summary
Severity: Medium
Advisory: BIT-superset-2026-23983
Aliases: CVE-2026-23983, GHSA-h294-8fxm-m2pj, PYSEC-2026-2375
Ecosystem: Bitnami
Published: 2026-02-26
Source: https://osv.dev/vulnerability/BIT-superset-2026-23983
Type: osv

## Affected
- Bitnami: `superset` — affected >=0 <6.0.0

## Details
A Sensitive Data Exposure vulnerability exists in Apache Superset allowing authenticated users to retrieve sensitive user information. The Tag endpoint (disabled by default) allows users to retrieve a list of objects associated with a specific tag.
When these associated objects include Users, the API response improperly serializes and returns sensitive fields, including password hashes (pbkdf2), email addresses, and login statistics. This vulnerability allows authenticated users with low privileges (e.g., Gamma role) to view sensitive authentication data 

This issue affects Apache Superset: before 6.0.0.

Users are recommended to upgrade to version 6.0.0, which fixes the issue or make sure TAGGING_SYSTEM is False (Apache Superset current default)

## References
- http://www.openwall.com/lists/oss-security/2026/02/24/7
- https://lists.apache.org/thread/62mgbc5hc8026skp69kb6vqozj3pr5ww
- https://nvd.nist.gov/vuln/detail/CVE-2026-23983
