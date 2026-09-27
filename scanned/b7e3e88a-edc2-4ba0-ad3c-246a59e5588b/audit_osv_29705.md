# [M] Apache Druid: Users can provide MySQL JDBC properties not on allow list

## Summary
Severity: Medium
Advisory: CVE-2024-45537
Aliases: GHSA-jh66-3545-vpm7
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-09-17
Source: https://osv.dev/vulnerability/CVE-2024-45537
Type: osv

## Details
Apache Druid allows users with certain permissions to read data from other database systems using JDBC. This functionality allows trusted users to set up Druid lookups or run ingestion tasks. Druid also allows administrators to configure a list of allowed properties that users are able to provide for their JDBC connections. By default, this allowed properties list restricts users to TLS-related properties only. However, when configuration a MySQL JDBC connection, users can use a particularly-crafted JDBC connection string to provide properties that are not on this allow list.

Users without the permission to configure JDBC connections are not able to exploit this vulnerability.
CVE-2021-26919 describes a similar vulnerability which was partially addressed in Apache Druid 0.20.2.

This issue is fixed in Apache Druid 30.0.1.

## References
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45537.json
- https://lists.apache.org/thread/2ovx1t77y6tlkhk5b42clp4vwo4c8cjv
- https://nvd.nist.gov/vuln/detail/CVE-2024-45537
