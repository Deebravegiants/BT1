# [C] Apache Sling Commons JSON bundle vulnerable to Improper Input Validation

## Summary
Severity: Critical
Advisory: GHSA-8j28-34qq-gmch
CVE: CVE-2022-47937
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-15
Source: https://github.com/advisories/GHSA-8j28-34qq-gmch
Type: github-advisory

## Affected
- Maven: `org.apache.sling:org.apache.sling.commons.json` — affected >=0

## Details
Improper input validation in the Apache Sling Commons JSON bundle allows an attacker to trigger unexpected errors by supplying specially-crafted input.

NOTE: This vulnerability only affects products that are no longer supported by the maintainer. The org.apache.sling.commons.json bundle has been deprecated as of March 2017 and should not be used anymore. Consumers are encouraged to consider the Apache Sling Commons Johnzon OSGi bundle provided by the Apache Sling project, but may of course use other JSON libraries.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-47937
- https://github.com/apache/sling-org-apache-sling-commons-johnzon
- https://issues.apache.org/jira/browse/SLING-6536
- https://lists.apache.org/thread/sws7z50x47gv0c38q4kx6ktqrvrrg1pm
- https://www.openwall.com/lists/oss-security/2023/05/15/2
- http://www.openwall.com/lists/oss-security/2023/05/15/2
