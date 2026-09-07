# [M] Apache ActiveMQ Cross-site scripting (XSS) vulnerability in the Portfolio publisher servlet 

## Summary
Severity: Medium
Advisory: GHSA-c9gx-27hq-wcvj
CVE: CVE-2013-1880
CWE: CWE-79
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-c9gx-27hq-wcvj
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:activemq-core` — affected >=0 <5.9.0

## Details
Cross-site scripting (XSS) vulnerability in the Portfolio publisher servlet in the demo web application in Apache ActiveMQ before 5.9.0 allows remote attackers to inject arbitrary web script or HTML via the refresh parameter to demo/portfolioPublish, a different vulnerability than CVE-2012-6092.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1880
- https://github.com/apache/activemq/commit/fafd12dfd4f71336f8e32c090d40ed1445959b40
- https://bugzilla.redhat.com/show_bug.cgi?id=924447
- https://github.com/apache/activemq
- https://issues.apache.org/jira/browse/AMQ-4398
- http://rhn.redhat.com/errata/RHSA-2013-1029.html
- http://www.securityfocus.com/bid/65615
