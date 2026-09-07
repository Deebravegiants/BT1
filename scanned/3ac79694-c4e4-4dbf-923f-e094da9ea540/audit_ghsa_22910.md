# [M] Apache Tomcat Example Application CSRF and XSS Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-g77g-vjjm-x83j
CVE: CVE-2007-4724
CWE: CWE-352
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-g77g-vjjm-x83j
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=0

## Details
Cross-site request forgery (CSRF) vulnerability in cal2.jsp in the calendar examples application in Apache Tomcat 4.1.31 allows remote attackers to add events as arbitrary users via the time and description parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-4724
- https://web.archive.org/web/20070911063436/http://securityreason.com/securityalert/3094
- https://web.archive.org/web/20081006123851/http://archives.neohapsis.com/archives/bugtraq/2007-09/0040.html
- https://web.archive.org/web/20200526022330/http://www.securityfocus.com/archive/1/478491/100/0/threaded
