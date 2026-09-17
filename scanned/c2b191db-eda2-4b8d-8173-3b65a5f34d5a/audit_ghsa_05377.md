# [H] Apache Hadoop HDFS Native Client has Out-of-bounds Write Vulnerability 

## Summary
Severity: High
Advisory: GHSA-92cc-952p-v8rh
CVE: CVE-2025-27821
CWE: CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-01-26
Source: https://github.com/advisories/GHSA-92cc-952p-v8rh
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-hdfs-native-client` — affected >=3.2.0 <3.4.2

## Details
Out-of-bounds Write vulnerability in Apache Hadoop HDFS native client.

This issue affects Apache Hadoop: from 3.2.0 before 3.4.2.

Users are recommended to upgrade to version 3.4.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27821
- https://github.com/apache/hadoop/pull/7481
- https://github.com/apache/hadoop/commit/2b32e46f666c7645f5d1e026be3982b99319ccb8
- https://github.com/apache/hadoop
- https://issues.apache.org/jira/browse/HDFS-17754
- https://lists.apache.org/thread/kwjhyyx0wl2z9b0mw0styjk0hhdbyplh
- http://www.openwall.com/lists/oss-security/2026/01/23/7
