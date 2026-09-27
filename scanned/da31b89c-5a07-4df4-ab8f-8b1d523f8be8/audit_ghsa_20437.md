# [M] Path traversal in Apache Karaf

## Summary
Severity: Medium
Advisory: GHSA-544x-2jx9-4pfg
CVE: CVE-2022-22932
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-01-28
Source: https://github.com/advisories/GHSA-544x-2jx9-4pfg
Type: github-advisory

## Affected
- Maven: `org.apache.karaf:apache-karaf` — affected >=4.3.0 <4.3.6
- Maven: `org.apache.karaf:apache-karaf` — affected >=0 <4.2.15

## Details
Apache Karaf obr:* commands and run goal on the karaf-maven-plugin have partial path traversal which allows to break out of expected folder. The risk is low as obr:* commands are not very used and the entry is set by user. This has been fixed in revision: https://gitbox.apache.org/repos/asf?p=karaf.git;h=36a2bc4 https://gitbox.apache.org/repos/asf?p=karaf.git;h=52b70cf Mitigation: Apache Karaf users should upgrade to 4.2.15 or 4.3.6 or later as soon as possible, or use correct path. JIRA Tickets: https://issues.apache.org/jira/browse/KARAF-7326

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22932
- https://github.com/apache/karaf/pull/1485
- https://gitbox.apache.org/repos/asf?p=karaf.git;h=36a2bc4
- https://gitbox.apache.org/repos/asf?p=karaf.git;h=52b70cf
- https://github.com/apache/karaf
- https://issues.apache.org/jira/browse/KARAF-7326
- https://karaf.apache.org/security/cve-2022-22932.txt
