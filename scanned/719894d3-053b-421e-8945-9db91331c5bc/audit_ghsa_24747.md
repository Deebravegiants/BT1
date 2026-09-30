# [M] Apache Tomcat Path Traversal Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m8h8-6rvg-f4mg
CVE: CVE-2008-2370
CWE: CWE-22
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-m8h8-6rvg-f4mg
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=4.1.0 <4.1.38
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.0 <5.5.27
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.18

## Details
Apache Tomcat 4.1.0 through 4.1.37, 5.5.0 through 5.5.26, and 6.0.0 through 6.0.16, when a `RequestDispatcher` is used, performs path normalization before removing the query string from the URI, which allows remote attackers to conduct directory traversal attacks and read arbitrary files via a `..` (dot dot) in a request parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-2370
- https://exchange.xforce.ibmcloud.com/vulnerabilities/44156
- https://web.archive.org/web/20090201124638/http://secunia.com/advisories/32120
- https://web.archive.org/web/20090201124957/http://secunia.com/advisories/31982
- https://web.archive.org/web/20090201125002/http://secunia.com/advisories/32266
- https://web.archive.org/web/20090201141000/http://secunia.com/advisories/32222
- https://web.archive.org/web/20090207111236/http://secunia.com/advisories/33797
- https://web.archive.org/web/20090225175903/http://secunia.com/advisories/33999
- https://web.archive.org/web/20090228074535/http://secunia.com/advisories/31379
- https://web.archive.org/web/20090228074540/http://secunia.com/advisories/34013
- https://web.archive.org/web/20090308065055/http://secunia.com/advisories/31865
- https://web.archive.org/web/20090811003155/http://secunia.com/advisories/35393
- https://web.archive.org/web/20090828023853/http://secunia.com/advisories/36249
- https://web.archive.org/web/20100706231759/http://secunia.com/advisories/37460
- https://web.archive.org/web/20110714083521/http://www.securitytracker.com/id?1020623
- https://web.archive.org/web/20110714174318/http://www.securityfocus.com/bid/30494
- https://web.archive.org/web/20120719164745/http://www.securityfocus.com/archive/1/495022/100/0/threaded
- https://web.archive.org/web/20120724210029/http://www.securityfocus.com/bid/31681
- https://web.archive.org/web/20140723000733/http://secunia.com/advisories/57126
- https://web.archive.org/web/20150621204350/http://www.securityfocus.com/archive/1/507985/100/0/threaded
