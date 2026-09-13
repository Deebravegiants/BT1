# [M] Apache Ambari XML External Entity injection

## Summary
Severity: Medium
Advisory: GHSA-qrp9-23p7-g5mf
CVE: CVE-2023-50380
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-27
Source: https://github.com/advisories/GHSA-qrp9-23p7-g5mf
Type: github-advisory

## Affected
- Maven: `org.apache.ambari.contrib.views:wfmanager` — affected >=2.7.0 <2.7.8

## Details
XML External Entity injection in Apache Ambari versions <= 2.7.7, Users are recommended to upgrade to version 2.7.8, which fixes this issue.

More Details:

Oozie Workflow Scheduler had a vulnerability that allowed for root-level file reading and privilege escalation from low-privilege users. The vulnerability was caused through lack of proper user input validation.

This vulnerability is known as an XML External Entity (XXE) injection attack. Attackers can exploit XXE vulnerabilities to read arbitrary files on the server, including sensitive system files. In theory, it might be possible to use this to escalate privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50380
- https://github.com/apache/ambari/commit/d9652e4611ea36208d5f748028b3a9cd980e6edb
- https://github.com/apache/ambari
- https://lists.apache.org/thread/qrt7mq7v7zyrh1qsh1gkg1m7clysvy32
- http://www.openwall.com/lists/oss-security/2024/02/27/6
