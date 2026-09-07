# [H] Apache Ozone user impersonation due to non-validation of Ozone S3 tokens

## Summary
Severity: High
Advisory: GHSA-5993-wwpg-m92c
CVE: CVE-2021-39236
CWE: CWE-862, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-5993-wwpg-m92c
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-ozone-ozone-manager` — affected >=0 <1.2.0

## Details
In Apache Ozone before 1.2.0, Authenticated users with valid Ozone S3 credentials can create specific OM requests, impersonating any other user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-39236
- https://github.com/apache/ozone/pull/1871
- https://github.com/apache/ozone/commit/60e078729e18ef1be276f35659957ac553d266f7
- https://github.com/apache/ozone
- https://issues.apache.org/jira/browse/HDDS-4763
- https://lists.apache.org/thread/q0lhspolnwfbsw33w98b7b1923n1np4d
- https://mail-archives.apache.org/mod_mbox/ozone-dev/202111.mbox/%3C0fd74baa-88a0-39a2-8f3a-b982acb25d5a%40apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/11/19/7
