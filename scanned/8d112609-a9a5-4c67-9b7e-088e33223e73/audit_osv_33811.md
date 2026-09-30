# [H] CVE-2025-50466

## Summary
Severity: High
Advisory: CVE-2025-50466
CVSS: 7.1 (CVSS:3.1/AC:L/AV:N/A:N/C:H/I:L/PR:L/S:U/UI:N)
Published: 2025-08-08
Source: https://osv.dev/vulnerability/CVE-2025-50466
Type: osv

## Details
OpenMetadata <=1.4.4 is vulnerable to SQL Injection. An attacker can extract information from the database in function listCount in the TestDefinitionDAO interface. The entityType parameter can be used to build a SQL query.

## References
- https://gist.github.com/javadk/aa7b5eb6f0fca2fbc334129b7572c7c6
- https://github.com/open-metadata/OpenMetadata/blob/4b9145a9da7ed95b7f868ab9f351e3d759af47d7/openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/CollectionDAO.java#L3521
- https://github.com/open-metadata/OpenMetadata/blob/4b9145a9da7ed95b7f868ab9f351e3d759af47d7/openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/CollectionDAO.java#L3522
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50466.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-50466
