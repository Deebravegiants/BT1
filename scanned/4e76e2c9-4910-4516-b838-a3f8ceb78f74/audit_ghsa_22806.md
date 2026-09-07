# [M] Apache Geode vulnerable to Exposure of Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-vh98-fqfc-4hj3
CVE: CVE-2017-9797
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vh98-fqfc-4hj3
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-core` — affected >=1.0.0 <1.2.1

## Details
When an Apache Geode cluster before v1.2.1 is operating in secure mode, an unauthenticated client can enter multi-user authentication mode and send metadata messages. These metadata operations could leak information about application data types. In addition, an attacker could perform a denial of service attack on the cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9797
- https://cwiki.apache.org/confluence/display/GEODE/Release+Notes#ReleaseNotes-SecurityVulnerabilities
- https://issues.apache.org/jira/browse/GEODE-3249
- http://mail-archives.apache.org/mod_mbox/geode-user/201709.mbox/%3cCAEwge-Hrbb7JS8Nygrh7geyFvW4bMZ3AdCmPOzMfvbniipz0bA@mail.gmail.com%3e
