# [H] Hive Metastore Server is vulnerable to SQL Injection

## Summary
Severity: High
Advisory: GHSA-932v-x9x2-vq29
CVE: CVE-2025-62728
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-26
Source: https://github.com/advisories/GHSA-932v-x9x2-vq29
Type: github-advisory

## Affected
- Maven: `org.apache.hive:hive-common` — affected >=4.1.0 <4.2.0
- Maven: `org.apache.hive:hive-metastore` — affected >=4.1.0 <4.2.0

## Details
SQL injection vulnerability in Hive Metastore Server (HMS) when processing delete column statistics requests via the Thrift APIs. The vulnerability is only exploitable by trusted/authorized users/applications that are allowed to call directly the Thrift APIs. In most real-world deployments, HMS is accessible to only a handful of applications (e.g., Hiveserver2) thus the vulnerability is not exploitable. Moreover, the vulnerable code cannot be reached when metastore.try.direct.sql property is set to false.

This issue affects Apache Hive: from 4.1.0 before 4.2.0.

Users are recommended to upgrade to version 4.2.0, which fixes the issue. Users who cannot upgrade directly are encouraged to set metastore.try.direct.sql property to false if the HMS Thrift APIs are exposed to general public.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62728
- https://github.com/apache/hive/commit/c18d0df2702130cf5d0f050e516eb8999aa56301
- https://github.com/apache/hive
- https://issues.apache.org/jira/browse/HIVE-29269
- https://lists.apache.org/thread/yj65dd8dmzgy8p3nv8zy33v8knzg9o7g
- http://www.openwall.com/lists/oss-security/2025/11/26/3
