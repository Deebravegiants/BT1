# [C] Apache Ambari Improper Access Control

## Summary
Severity: Critical
Advisory: GHSA-j76q-99x2-v7vq
CVE: CVE-2016-6807
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j76q-99x2-v7vq
Type: github-advisory

## Affected
- Maven: `org.apache.ambari:ambari` — affected >=2.4.0 <2.4.2

## Details
Custom commands may be executed on Ambari Agent (2.4.x, before 2.4.2) hosts without authorization, leading to unauthorized access to operations that may affect the underlying system. Such operations are invoked by the Ambari Agent process on Ambari Agent hosts, as the user executing the Ambari Agent process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6807
- https://cwiki.apache.org/confluence/display/AMBARI/Ambari+Vulnerabilities#AmbariVulnerabilities-FixedinAmbari2.4.2
- https://github.com/apache/ambari
- https://web.archive.org/web/20200227181557/http://www.securityfocus.com/bid/97184
