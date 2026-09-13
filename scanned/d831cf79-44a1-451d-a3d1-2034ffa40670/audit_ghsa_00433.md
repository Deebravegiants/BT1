# [H] Apache Camel's Validation Component is vulnerable against SSRF via remote DTDs and XXE.

## Summary
Severity: High
Advisory: GHSA-vq9j-jh62-5hmp
CVE: CVE-2017-5643
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-vq9j-jh62-5hmp
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-core` — affected >=0 <2.17.6
- Maven: `org.apache.camel:camel-core` — affected >=2.18.0 <2.18.2

## Details
Description: The Validation Component of Apache Camel evaluates DTD headers of XML stream sources, although a validation against XML schemas (XSD) is executed. Remote attackers can use this feature to make Server-Side Request Forgery (SSRF) attacks by sending XML documents with remote DTDs URLs or XML External Entities (XXE).  The vulnerability is not given for SAX or StAX sources.

Mitigation: 2.17.x users should upgrade to 2.17.6, 2.18.x users should upgrade to 2.18.3. 

The JIRA tickets https://issues.apache.org/jira/browse/CAMEL-10894 refers to the various commits that resolved the issue, and have more details.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5643
- https://github.com/apache/camel/commit/2c6964ae94d8f9a9c9a32e5ae5a0b794e8b8d3be
- https://github.com/apache/camel/commit/8afc5d1757795fde715902067360af5d90f046da
- https://github.com/apache/camel/commit/9f7376abbff7434794f2c7c2909e02bac232fb5b
- https://access.redhat.com/errata/RHSA-2017:1832
- https://github.com/advisories/GHSA-vq9j-jh62-5hmp
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-10894
- https://lists.apache.org/thread.html/2318d7f7d87724d8716cd650c21b31cb06e4d34f6d0f5ee42f28fdaf@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/b4014ea7c5830ca1fc28edd5cafedfe93ad4af2d9e69c961c5def31d@%3Ccommits.camel.apache.org%3E
- http://camel.apache.org/security-advisories.data/CVE-2017-5643.txt.asc?version=1&modificationDate=1489652454000&api=v2
- http://www.securityfocus.com/bid/97226
