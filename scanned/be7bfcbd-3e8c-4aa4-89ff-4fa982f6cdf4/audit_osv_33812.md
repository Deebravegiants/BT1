# [M] CVE-2025-50467

## Summary
Severity: Medium
Advisory: CVE-2025-50467
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-08-08
Source: https://osv.dev/vulnerability/CVE-2025-50467
Type: osv

## Details
OpenMetadata <=1.4.4 is vulnerable to SQL Injection. An attacker can extract information from the database in function listCount in the TestDefinitionDAO interface. The supportedDataTypeParam parameter can be used to build a SQL query.

## References
- https://gist.github.com/javadk/ed0d38e4578405672f154e289036a705
- https://github.com/open-metadata/OpenMetadata/blob/4b9145a9da7ed95b7f868ab9f351e3d759af47d7/openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/CollectionDAO.java#L3527
- https://github.com/open-metadata/OpenMetadata/blob/4b9145a9da7ed95b7f868ab9f351e3d759af47d7/openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/CollectionDAO.java#L3528
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50467.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-50467
