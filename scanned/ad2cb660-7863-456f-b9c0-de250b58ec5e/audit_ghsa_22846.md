# [M] Apache Struts's CookieInterceptor component does not use the parameter-name whitelist

## Summary
Severity: Medium
Advisory: GHSA-2ppp-xj34-vvf7
CVE: CVE-2012-0392
Ecosystem: Maven
Published: 2022-05-04
Source: https://github.com/advisories/GHSA-2ppp-xj34-vvf7
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=0 <2.2.3.1
- Maven: `org.apache.struts.xwork:xwork-core` — affected >=0 <2.2.3.1

## Details
The CookieInterceptor component in Apache Struts before 2.3.1.1 does not use the parameter-name whitelist, which allows remote attackers to execute arbitrary commands via a crafted HTTP Cookie header that triggers Java code execution through a static method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-0392
- https://github.com/apache/struts/commit/25e50069d60434a30395e3a98357ffba2bed427e
- https://github.com/apache/struts
- https://lists.immunityinc.com/pipermail/dailydave/2012-January/000011.html
- https://web.archive.org/web/20120612142634/https://sec-consult.com/files/20120104-0_Apache_Struts2_Multiple_Critical_Vulnerabilities.txt
- https://web.archive.org/web/20140723153720/http://secunia.com/advisories/47393
- http://archives.neohapsis.com/archives/bugtraq/2012-01/0031.html
- http://struts.apache.org/2.x/docs/s2-008.html
- http://struts.apache.org/2.x/docs/version-notes-2311.html
- http://www.exploit-db.com/exploits/18329
