# [M] Apache NiFi vulnerable to Deserialization of Untrusted Data

## Summary
Severity: Medium
Advisory: GHSA-65wh-g8x8-gm2h
CVE: CVE-2023-34212
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-06-12
Source: https://github.com/advisories/GHSA-65wh-g8x8-gm2h
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-jms-processors` — affected >=1.8.0 <1.22.0

## Details
The JndiJmsConnectionFactoryProvider Controller Service, along with the ConsumeJMS and PublishJMS Processors, in Apache NiFi 1.8.0 through 1.21.0 allow an authenticated and authorized user to configure URL and library properties that enable deserialization of untrusted data from a remote location.

The resolution validates the JNDI URL and restricts locations to a set of allowed schemes.

You are recommended to upgrade to version 1.22.0 or later which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34212
- https://github.com/apache/nifi/pull/7313
- https://github.com/apache/nifi/commit/3fcb82ee4509d1ad73893d8dca003be6d086c5d6
- https://github.com/apache/nifi
- https://issues.apache.org/jira/browse/NIFI-11614
- https://lists.apache.org/thread/w5rm46fxmvxy216tglf0dv83wo6gnzr5
- https://nifi.apache.org/security.html#CVE-2023-34212
- http://www.openwall.com/lists/oss-security/2023/06/12/2
