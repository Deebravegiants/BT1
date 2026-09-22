# [H] Trino: Iceberg REST catalog static and vended credentials are accessible via query JSON

## Summary
Severity: High
Advisory: GHSA-x27p-5f68-m644
CVE: CVE-2026-34214
CWE: CWE-212, CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-x27p-5f68-m644
Type: github-advisory

## Affected
- Maven: `io.trino:trino-iceberg` — affected >=439 <480

## Details
### Summary

Iceberg connector REST catalog static credentials (access key) or vended credentials (temporary access key) are accessible to users that have write privilege on SQL level.

### Details

Iceberg REST catalog typically needs access to object storage. This access can be configured in multiple different ways. When storage access is achieved by static credentials (e.g. AWS S3 access key) or vended credentials (temporary access key).

Query JSON is a query visualization and performance troubleshooting facility. It includes serialized query plan and handles for table writes or  execution of table procedures. A user that submitted a query has access to query JSON for their query. Query JSON is available from Trino UI or via `/ui/api/query/«query_id»` and `/v1/query/«query_id»` endpoints.

The storage credentials are stored in those handles when performing write operations, or table maintenance operations. They are serialized in query JSON. A user with write access to data in Iceberg connector configured to use REST Catalog with static or vended credentials can retrieve those credentials.

### Impact

Anyone using Iceberg REST catalog with static or vended credentials is impacted.
The credentials should be considered compromised. 
Vended credentials are temporary in nature so they do not need to be rotated. However, underlying data could have been exposed.

## References
- https://github.com/trinodb/trino/security/advisories/GHSA-x27p-5f68-m644
- https://nvd.nist.gov/vuln/detail/CVE-2026-34214
- https://github.com/trinodb/trino
- https://github.com/trinodb/trino/releases/tag/480
