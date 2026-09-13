# [M] Jakarta Tomcat Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w97x-xfxf-f9xj
CVE: CVE-2003-0045
CWE: CWE-400
Ecosystem: Maven
Published: 2022-04-29
Source: https://github.com/advisories/GHSA-w97x-xfxf-f9xj
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=0 <3.3.1a

## Details
Jakarta Tomcat before 3.3.1a on certain Windows systems may allow remote attackers to cause a denial of service (thread hang and resource consumption) via a request for a JSP page containing an MS-DOS device name, such as aux.jsp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2003-0045
- https://exchange.xforce.ibmcloud.com/vulnerabilities/12102
- http://jakarta.apache.org/builds/jakarta-tomcat/release/v3.3.1a/RELEASE-NOTES-3.3.1a.txt
