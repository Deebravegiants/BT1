# [M] Apache Tomcat is vulnerable to HTTP request-smuggling

## Summary
Severity: Medium
Advisory: GHSA-j448-j653-r3vj
CVE: CVE-2013-4286
CWE: CWE-20
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-j448-j653-r3vj
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=0 <6.0.39
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.47
- Maven: `org.apache.tomcat:tomcat` — affected >=8.0.0-RC1 <8.0.0-RC3

## Details
Apache Tomcat before 6.0.39, 7.x before 7.0.47, and 8.x before 8.0.0-RC3, when an HTTP connector or AJP connector is used, does not properly handle certain inconsistent HTTP request headers, which allows remote attackers to trigger incorrect identification of a request's length and conduct request-smuggling attacks via (1) multiple Content-Length headers or (2) a Content-Length header and a "Transfer-Encoding: chunked" header.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2005-2090.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4286
- https://github.com/apache/tomcat/commit/41b90b6ebc3e7f898a5a87d197ddf63790d33315
- https://github.com/apache/tomcat/commit/7c040003f1387795356605566be7870cf70e05dc
- https://github.com/apache/tomcat/commit/bcce3e4997a4ed06fe03e2517443f3ad8ade2dfa
- https://github.com/apache/tomcat/commit/d0b3e252eb168fafbfb4c3efc16d4192fc8fad6c
- https://github.com/apache/tomcat80/commit/ff00954b78e6484e40f323c0cef2e6d95c2882b9
- https://web.archive.org/web/20141230041748/http://seclists.org/fulldisclosure/2014/Dec/23
- https://web.archive.org/web/20160317145515/http://www.securityfocus.com/archive/1/534161/100/0/threaded
- https://web.archive.org/web/20160729061926/http://www.securityfocus.com/bid/65773
- https://web.archive.org/web/20161014054543/http://www-01.ibm.com/support/docview.wss?uid=swg21678231
- https://web.archive.org/web/20161014054838/http://www-01.ibm.com/support/docview.wss?uid=swg21677147
- https://web.archive.org/web/20161014054913/http://www-01.ibm.com/support/docview.wss?uid=swg21678113
- https://web.archive.org/web/20161014054948/http://www-01.ibm.com/support/docview.wss?uid=swg21667883
- https://web.archive.org/web/20161024215453/http://secunia.com/advisories/59873
- https://web.archive.org/web/20161024215639/http://secunia.com/advisories/59722
- https://web.archive.org/web/20161024215804/http://secunia.com/advisories/59675
- https://web.archive.org/web/20161024220018/http://secunia.com/advisories/59724
- https://web.archive.org/web/20161024220034/http://secunia.com/advisories/59733
- https://web.archive.org/web/20140804172142/http://secunia.com/advisories/59036
- https://web.archive.org/web/20140724174205/http://secunia.com/advisories/57675
