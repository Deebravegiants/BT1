# [H] OpenMetadata SQL Injection

## Summary
Severity: High
Advisory: GHSA-x8pm-wrg2-mqmx
CVE: CVE-2024-55238
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-04-17
Source: https://github.com/advisories/GHSA-x8pm-wrg2-mqmx
Type: github-advisory

## Affected
- Maven: `org.open-metadata:openmetadata-service` — affected >=0

## Details
OpenMetadata <=1.4.1 is vulnerable to SQL Injection. An attacker can extract information from the database in function listCount in the WorkflowDAO interface. The workflowtype and status parameters can be used to build a SQL query.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-55238
- https://github.com/open-metadata/OpenMetadata/commit/47a13e27cf24465c44044ac79654b87dde8d39a8
- https://gist.github.com/javadk/68c597cdb94768dab31a3219c2ad9904
- https://github.com/open-metadata/OpenMetadata
- https://github.com/open-metadata/OpenMetadata/blob/98945cb2db87ebb325d3a72131f049abffcba345/openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/CollectionDAO.java#L4243
- https://github.com/open-metadata/OpenMetadata/blob/98945cb2db87ebb325d3a72131f049abffcba345/openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/CollectionDAO.java#L4247
