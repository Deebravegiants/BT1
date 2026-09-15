# [H] Apache Tomcat DoS via Malicious Get Request

## Summary
Severity: High
Advisory: GHSA-pqr5-9v2j-44xg
CVE: CVE-2002-2272
CWE: CWE-119
Ecosystem: Maven
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-pqr5-9v2j-44xg
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=4.0.0

## Details
Tomcat 4.0 through 4.1.12, using mod_jk 1.2.1 module on Apache 1.3 through 1.3.27, allows remote attackers to cause a denial of service (desynchronized communications) via an HTTP GET request with a Transfer-Encoding chunked field with invalid values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2002-2272
- https://exchange.xforce.ibmcloud.com/vulnerabilities/10771
- https://web.archive.org/web/20030501051114/http://www.securityfocus.com/bid/6320
- https://web.archive.org/web/20051124132812/http://archives.neohapsis.com/archives/bugtraq/2002-12/0045.html
