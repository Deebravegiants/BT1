# [M] Apache Camel allows remote actor to read arbitrary files via external entity in invalid XML string or GenericFile object

## Summary
Severity: Medium
Advisory: GHSA-mhx2-r3jx-g94c
CVE: CVE-2015-0264
Ecosystem: Maven
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-mhx2-r3jx-g94c
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-core` — affected >=0 <2.13.4
- Maven: `org.apache.camel:camel-core` — affected >=2.14.0 <2.14.2

## Details
Multiple XML external entity (XXE) vulnerabilities in builder/xml/XPathBuilder.java in Apache Camel before 2.13.4 and 2.14.x before 2.14.2 allow remote attackers to read arbitrary files via an external entity in an invalid XML (1) String or (2) GenericFile object in an XPath query.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-0264
- https://github.com/apache/camel/commit/7360aada5154434c68774aa30e0f21ddc5f27b9f
- https://github.com/apache/camel/commit/b47b51a195b38e7ab7c099d19910af70a16638f6
- https://camel.apache.org/security-advisories.data/CVE-2015-0264.txt.asc
- https://git-wip-us.apache.org/repos/asf?p=camel.git;a=commitdiff;h=1df559649a96a1ca0368373387e542f46e4820da
- https://github.com/advisories/GHSA-mhx2-r3jx-g94c
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-8312
- https://lists.apache.org/thread.html/2318d7f7d87724d8716cd650c21b31cb06e4d34f6d0f5ee42f28fdaf@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/b4014ea7c5830ca1fc28edd5cafedfe93ad4af2d9e69c961c5def31d@%3Ccommits.camel.apache.org%3E
- http://rhn.redhat.com/errata/RHSA-2015-1041.html
- http://rhn.redhat.com/errata/RHSA-2015-1538.html
- http://rhn.redhat.com/errata/RHSA-2015-1539.html
- http://securitytracker.com/id/1032442
