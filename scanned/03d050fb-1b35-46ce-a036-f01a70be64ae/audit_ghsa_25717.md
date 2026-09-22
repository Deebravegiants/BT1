# [M] Apache Tomcat Allows Source Disclosure

## Summary
Severity: Medium
Advisory: GHSA-x445-mmpw-7r4f
CVE: CVE-2001-0590
CWE: CWE-200
Ecosystem: Maven
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-x445-mmpw-7r4f
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-servlet-api` — affected >=0 <3.2.2

## Details
Apache Software Foundation Tomcat Servlet prior to 3.2.2 allows a remote attacker to read the source code to arbitrary 'jsp' files via a malformed URL request which does not end with an HTTP protocol specification (i.e. HTTP/1.0).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2001-0590
- https://exchange.xforce.ibmcloud.com/vulnerabilities/6971
- https://web.archive.org/web/20020711002734/http://archives.neohapsis.com/archives/bugtraq/2001-04/0031.html
