# [M] Tomcat uses trusted privileges when processing web.xml file

## Summary
Severity: Medium
Advisory: GHSA-cvx5-7vc7-rg77
CVE: CVE-2003-0043
CWE: CWE-250
Ecosystem: Maven
Published: 2022-04-29
Source: https://github.com/advisories/GHSA-cvx5-7vc7-rg77
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=0 <3.3.1a

## Details
Jakarta Tomcat before 3.3.1a, when used with JDK 1.3.1 or earlier, uses trusted privileges when processing the web.xml file, which could allow remote attackers to read portions of some files through the web.xml file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2003-0043
- https://exchange.xforce.ibmcloud.com/vulnerabilities/11195
- https://github.com/apache/tomcat
- https://web.archive.org/web/20030804165204/http://jakarta.apache.org/builds/jakarta-tomcat/release/v3.3.1a/RELEASE-NOTES-3.3.1a.txt
- https://web.archive.org/web/20030810045410/http://jakarta.apache.org/builds/jakarta-tomcat/release/v3.3.1a
- https://web.archive.org/web/20030819144200/http://www.ciac.org/ciac/bulletins/n-060.shtml
- https://web.archive.org/web/20131213024606/http://www.securityfocus.com/bid/6722
- https://web.archive.org/web/20140627151430/http://www.securityfocus.com/advisories/5111
- http://www.debian.org/security/2003/dsa-246
