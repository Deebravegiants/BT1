# [M] Apache Camel XML External Entity vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3hrc-f439-727g
CVE: CVE-2015-0263
CWE: CWE-611
Ecosystem: Maven
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-3hrc-f439-727g
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-core` — affected >=0 <2.13.4
- Maven: `org.apache.camel:camel-core` — affected >=2.14.0 <2.14.2

## Details
XML external entity (XXE) vulnerability in the XML converter setup in converter/jaxp/XmlConverter.java in Apache Camel before 2.13.4 and 2.14.x before 2.14.2 allows remote attackers to read arbitrary files via an external entity in an SAXSource.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-0263
- https://github.com/apache/camel/commit/06db9e0744f2bb9f6e3bf16c0dfe7099a3481558
- https://github.com/apache/camel/commit/367d53e73c8b5a1e73c24423e631709f9a96e08d
- https://github.com/apache/camel/commit/7d19340bcdb42f7aae584d9c5003ac4f7ddaee36
- https://camel.apache.org/security-advisories.data/CVE-2015-0263.txt.asc
- https://git-wip-us.apache.org/repos/asf?p=camel.git;a=commitdiff;h=7d19340bcdb42f7aae584d9c5003ac4f7ddaee36
- https://github.com/advisories/GHSA-3hrc-f439-727g
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-8312
- https://lists.apache.org/thread.html/2318d7f7d87724d8716cd650c21b31cb06e4d34f6d0f5ee42f28fdaf@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/b4014ea7c5830ca1fc28edd5cafedfe93ad4af2d9e69c961c5def31d@%3Ccommits.camel.apache.org%3E
- http://rhn.redhat.com/errata/RHSA-2015-1041.html
- http://rhn.redhat.com/errata/RHSA-2015-1538.html
- http://rhn.redhat.com/errata/RHSA-2015-1539.html
- http://www.securitytracker.com/id/1032442
