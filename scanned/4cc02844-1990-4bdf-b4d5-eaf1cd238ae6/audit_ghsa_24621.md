# [C] Apache Camel camel-hessian component vulnerable to Java object deserialization

## Summary
Severity: Critical
Advisory: GHSA-5whj-523x-6j68
CVE: CVE-2017-12633
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-5whj-523x-6j68
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-hessian` — affected >=2.0 <2.19.4
- Maven: `org.apache.camel:camel-hessian` — affected >=2.20.0 <2.20.1

## Details
The camel-hessian component in Apache Camel 2.x before 2.19.4 and 2.20.x before 2.20.1 is vulnerable to Java object de-serialisation vulnerability. De-serializing untrusted data can lead to security flaws.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12633
- https://access.redhat.com/errata/RHSA-2018:0319
- https://issues.apache.org/jira/browse/CAMEL-11923
- https://lists.apache.org/thread.html/2318d7f7d87724d8716cd650c21b31cb06e4d34f6d0f5ee42f28fdaf@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/b4014ea7c5830ca1fc28edd5cafedfe93ad4af2d9e69c961c5def31d@%3Ccommits.camel.apache.org%3E
- http://camel.apache.org/security-advisories.data/CVE-2017-12633.txt.asc
- http://www.securityfocus.com/bid/101874
