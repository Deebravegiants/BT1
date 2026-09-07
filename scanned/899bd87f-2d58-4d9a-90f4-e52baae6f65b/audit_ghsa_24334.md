# [M] Apache ActiveMQ Sensitive Information Disclosure via the Jetty ResourceHandler

## Summary
Severity: Medium
Advisory: GHSA-v2c9-9m8v-8jjm
CVE: CVE-2010-1587
CWE: CWE-20
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-v2c9-9m8v-8jjm
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:activemq-web-console` — affected >=5.0.0 <5.3.2

## Details
The Jetty ResourceHandler in Apache ActiveMQ 5.x before 5.3.2 and 5.4.x before 5.4.0 allows remote attackers to read JSP source code via a // (slash slash) initial substring in a URI for (1) admin/index.jsp, (2) admin/queues.jsp, or (3) admin/topics.jsp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-1587
- https://github.com/apache/activemq/commit/aadd17ab7b6b6a664322538d25ee96dad67616e0
- https://github.com/apache/activemq
- https://github.com/apache/activemq/compare/activemq-5.3.1...activemq-parent-5.3.2
- https://github.com/apache/activemq/tree/main/activemq-web-console/src/main/webapp
- https://issues.apache.org/activemq/browse/AMQ-2700
- https://web.archive.org/web/20100426064914/http://www.vupen.com/english/advisories/2010/0979
- https://web.archive.org/web/20100702082040/http://secunia.com/advisories/39567
- https://web.archive.org/web/20150314050810/http://archives.neohapsis.com/archives/fulldisclosure/2010-04/0278.html
- https://web.archive.org/web/20200228044456/http://www.securityfocus.com/bid/39636
- https://web.archive.org/web/20201208002259/http://www.securityfocus.com/archive/1/510896/100/0/threaded
