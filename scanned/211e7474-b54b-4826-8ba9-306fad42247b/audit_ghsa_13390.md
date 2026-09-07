# [C] SQL injection in audit endpoint

## Summary
Severity: Critical
Advisory: GHSA-r5pv-7g89-cxmc
CVE: CVE-2023-35088
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-r5pv-7g89-cxmc
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-service` — affected >=1.4.0 <1.8.0

## Details
Improper Neutralization of Special Elements Used in an SQL Command ('SQL Injection') vulnerability in Apache Software Foundation Apache InLong.This issue affects Apache InLong: from 1.4.0 through 1.7.0. 
In the toAuditCkSql method, the groupId, streamId, auditId, and dt are directly concatenated into the SQL query statement, which may lead to SQL injection attacks.
Users are advised to upgrade to Apache InLong's 1.8.0 or cherry-pick [1] to solve it.

[1]  https://github.com/apache/inlong/pull/8198

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35088
- https://github.com/apache/inlong/pull/8198
- https://github.com/apache/inlong/commit/cab63a8eea6c0f4bf3d30ce245b7e1beee42504d
- https://github.com/apache/inlong
- https://lists.apache.org/thread/os7b66x4n8dbtrdpb7c6x37bb1vjb0tk
- http://seclists.org/fulldisclosure/2023/Jul/43
- http://www.openwall.com/lists/oss-security/2023/07/25/4
