# [H] Apache Ranger Hive Plugin missing permissions check

## Summary
Severity: High
Advisory: GHSA-vjr2-wpfh-5r9p
CVE: CVE-2021-40331
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-05-05
Source: https://github.com/advisories/GHSA-vjr2-wpfh-5r9p
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger-hive-plugin` — affected >=2.0.0 <2.4.0

## Details
An Incorrect Permission Assignment for Critical Resource vulnerability was found in the Apache Ranger Hive Plugin. Any user with SELECT privilege on a database can alter the ownership of the table in Hive when Apache Ranger Hive Plugin is enabled
This issue affects Apache Ranger Hive Plugin: from 2.0.0 through 2.3.0. Users are recommended to upgrade to version 2.4.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40331
- https://github.com/apache/ranger/commit/7dec3015ec82b69ba8f724410f12dfce2480cccd
- https://github.com/apache/ranger/commit/9115a20d524ba9173ce5db3e270c385d58d8aeab
- https://github.com/apache/ranger
- https://issues.apache.org/jira/browse/RANGER-3357
- https://issues.apache.org/jira/browse/RANGER-3474
- https://lists.apache.org/thread/s68yls6cnkdmzn1k4hqt50vs6wjvt2rn
