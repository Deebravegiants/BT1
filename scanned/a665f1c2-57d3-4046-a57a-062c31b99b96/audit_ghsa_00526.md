# [H] Apache Camel's XSLT component allows remote attackers to execute arbitrary Java methods

## Summary
Severity: High
Advisory: GHSA-h6rp-8v4j-hwph
CVE: CVE-2014-0003
CWE: CWE-502
Ecosystem: Maven
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-h6rp-8v4j-hwph
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-core` — affected >=2.11.0 <2.11.4
- Maven: `org.apache.camel:camel-core` — affected >=2.12.0 <2.12.3

## Details
The XSLT component in Apache Camel 2.11.x before 2.11.4, 2.12.x before 2.12.3, and possibly earlier versions allows remote attackers to execute arbitrary Java methods via a crafted message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0003
- https://github.com/apache/camel/commit/483b445dc77487e2d0f3d8c8bf1a7bbab04464c
- https://github.com/apache/camel/commit/c6de749e9b3c7b61861c5480e91550290585224
- https://github.com/apache/camel/commit/e922f89290f236f3107039de61af0375826bd96d
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-7123
- https://lists.apache.org/thread.html/2318d7f7d87724d8716cd650c21b31cb06e4d34f6d0f5ee42f28fdaf%40%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/2318d7f7d87724d8716cd650c21b31cb06e4d34f6d0f5ee42f28fdaf@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/b4014ea7c5830ca1fc28edd5cafedfe93ad4af2d9e69c961c5def31d%40%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/b4014ea7c5830ca1fc28edd5cafedfe93ad4af2d9e69c961c5def31d@%3Ccommits.camel.apache.org%3E
- https://web.archive.org/web/20200229061309/http://www.securityfocus.com/bid/65902
- http://camel.apache.org/security-advisories.data/CVE-2014-0003.txt.asc
- http://rhn.redhat.com/errata/RHSA-2014-0245.html
- http://rhn.redhat.com/errata/RHSA-2014-0254.html
- http://rhn.redhat.com/errata/RHSA-2014-0371.html
- http://rhn.redhat.com/errata/RHSA-2014-0372.html
