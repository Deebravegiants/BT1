# [M] Denial of service in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-wf5v-jhxj-q632
CVE: CVE-2014-0095
CWE: CWE-20
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wf5v-jhxj-q632
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=8.0.0-RC1 <8.0.4
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.0.0-RC1 <8.0.4

## Details
java/org/apache/coyote/ajp/AbstractAjpProcessor.java in Apache Tomcat 8.x before 8.0.4 allows remote attackers to cause a denial of service (thread consumption) by using a "Content-Length: 0" AJP request to trigger a hang in request processing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0095
- https://github.com/apache/tomcat/commit/8884dae60ace77a87ed9385442ce429e98c3a479
- https://github.com/apache/tomcat80/commit/77590c897f0e542fe363d70efdf3b82209510aee
- https://github.com/apache/tomcat
- https://web.archive.org/web/20140713043210/http://www.securitytracker.com/id/1030300
- https://web.archive.org/web/20141126170141/http://www.securityfocus.com/bid/67673
- https://web.archive.org/web/20151017043748/http://secunia.com/advisories/60729
- https://web.archive.org/web/20161024215453/http://secunia.com/advisories/59873
- http://seclists.org/fulldisclosure/2014/May/134
- http://svn.apache.org/viewvc?view=revision&revision=1578392
- http://tomcat.apache.org/security-8.html
- http://www-01.ibm.com/support/docview.wss?uid=swg21678231
- http://www-01.ibm.com/support/docview.wss?uid=swg21681528
- http://www.oracle.com/technetwork/topics/security/cpuoct2014-1972960.html
