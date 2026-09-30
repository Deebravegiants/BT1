# [M] Apache Commons Configuration: StackOverflowError calling ListDelimiterHandler.flatten(Object, int) with a cyclical object tree

## Summary
Severity: Medium
Advisory: GHSA-9w38-p64v-xpmv
CVE: CVE-2024-29133
CWE: CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-03-21
Source: https://github.com/advisories/GHSA-9w38-p64v-xpmv
Type: github-advisory

## Affected
- Maven: `org.apache.commons:commons-configuration2` — affected >=2.0 <2.10.1

## Details
This Out-of-bounds Write vulnerability in Apache Commons Configuration affects Apache Commons Configuration: from 2.0 before 2.10.1. User can see this as a 'StackOverflowError' calling 'ListDelimiterHandler.flatten(Object, int)' with a cyclical object tree.
Users are recommended to upgrade to version 2.10.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29133
- https://github.com/apache/commons-configuration/commit/43f4dab021e9acb8db390db2ae80aa0cee4f9ee4
- https://issues.apache.org/jira/browse/CONFIGURATION-841
- https://lists.apache.org/thread/ccb9w15bscznh6tnp3wsvrrj9crbszh2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SNKDKEEKZNL5FGCTZKJ6CFXFVWFL5FJ7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YD4AFTIIQW662LUAQRMWS6BBKYSZG3YS
- apache/commons-configuration
- http://www.openwall.com/lists/oss-security/2024/03/20/3
