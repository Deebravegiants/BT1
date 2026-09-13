# [M] Jakarta Tomcat Directory Listing vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qfw2-wvrw-mvw4
CVE: CVE-2003-0042
CWE: CWE-22
Ecosystem: Maven
Published: 2022-04-29
Source: https://github.com/advisories/GHSA-qfw2-wvrw-mvw4
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=0 <3.3.1a

## Details
Jakarta Tomcat before 3.3.1a, when used with JDK 1.3.1 or earlier, allows remote attackers to list directories even with an index.html or other file present, or obtain unprocessed source code for a JSP file, via a URL containing a null character.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2003-0042
- https://exchange.xforce.ibmcloud.com/vulnerabilities/11194
- https://github.com/apache/tomcat
- http://jakarta.apache.org/builds/jakarta-tomcat/release/v3.3.1a
- http://jakarta.apache.org/builds/jakarta-tomcat/release/v3.3.1a/RELEASE-NOTES-3.3.1a.txt
- http://marc.info/?l=bugtraq&m=104394568616290&w=2
- http://secunia.com/advisories/7972
- http://secunia.com/advisories/7977
- http://www.ciac.org/ciac/bulletins/n-060.shtml
- http://www.debian.org/security/2003/dsa-246
- http://www.securityfocus.com/advisories/5111
- http://www.securityfocus.com/bid/6721
