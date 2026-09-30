# [H] Apache InLong has Files or Directories Accessible to External Parties

## Summary
Severity: High
Advisory: GHSA-3p9p-59qf-mqwh
CVE: CVE-2023-31064
CWE: CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-3p9p-59qf-mqwh
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-workflow` — affected >=1.2.0 <1.7.0

## Details
Files or Directories Accessible to External Parties vulnerability in Apache Software Foundation Apache InLong. This issue affects Apache InLong from 1.2.0 through 1.6.0.The user in InLong could cancel an application that doesn't belong to it. Users are advised to upgrade to Apache InLong's 1.7.0 or cherry-pick https://github.com/apache/inlong/pull/7799 to solve it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31064
- https://github.com/apache/inlong/pull/7799
- https://github.com/apache/inlong
- https://lists.apache.org/thread/1osd2k3t3qol2wdsswqtr9gxdkf78n00
