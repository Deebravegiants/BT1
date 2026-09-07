# [M] Apache Commons Configuration: StackOverflowError adding property in AbstractListDelimiterHandler.flattenIterator()

## Summary
Severity: Medium
Advisory: GHSA-xjp4-hw94-mvp5
CVE: CVE-2024-29131
CWE: CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-03-21
Source: https://github.com/advisories/GHSA-xjp4-hw94-mvp5
Type: github-advisory

## Affected
- Maven: `org.apache.commons:commons-configuration2` — affected >=2.0 <2.10.1

## Details
This Out-of-bounds Write vulnerability in Apache Commons Configuration affects Apache Commons Configuration: from 2.0 before 2.10.1. User can see this as a 'StackOverflowError' when adding a property in 'AbstractListDelimiterHandler.flattenIterator()'.
Users are recommended to upgrade to version 2.10.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29131
- https://github.com/apache/commons-configuration/commit/56b5c4dcdffbde27870df5a3105d6a5f9b22f554
- https://github.com/apache/commons-configuration
- https://issues.apache.org/jira/browse/CONFIGURATION-840
- https://lists.apache.org/thread/03nzzzjn4oknyw5y0871tw7ltj0t3r37
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SNKDKEEKZNL5FGCTZKJ6CFXFVWFL5FJ7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YD4AFTIIQW662LUAQRMWS6BBKYSZG3YS
- https://security.netapp.com/advisory/ntap-20241213-0001
- http://www.openwall.com/lists/oss-security/2024/03/20/4
