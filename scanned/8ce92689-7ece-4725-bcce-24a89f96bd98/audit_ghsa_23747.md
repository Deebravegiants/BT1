# [C] Command injection in Apache Maven maven-shared-utils

## Summary
Severity: Critical
Advisory: GHSA-rhgr-952r-6p8q
CVE: CVE-2022-29599
CWE: CWE-116, CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rhgr-952r-6p8q
Type: github-advisory

## Affected
- Maven: `org.apache.maven.shared:maven-shared-utils` — affected >=0 <3.3.3

## Details
In Apache Maven maven-shared-utils prior to version 3.3.3, the Commandline class can emit double-quoted strings without proper escaping, allowing shell injection attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29599
- https://github.com/apache/maven-shared-utils/pull/40
- https://github.com/apache/maven-shared-utils
- https://issues.apache.org/jira/browse/MSHARED-297
- https://lists.debian.org/debian-lts-announce/2022/08/msg00018.html
- https://www.debian.org/security/2022/dsa-5242
- http://www.openwall.com/lists/oss-security/2022/05/23/3
