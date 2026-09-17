# [M] Jetty HTTP Server Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-p5rr-q5g6-gm42
CVE: CVE-2004-2381
CWE: CWE-400
Ecosystem: Maven
Published: 2022-04-29
Source: https://github.com/advisories/GHSA-p5rr-q5g6-gm42
Type: github-advisory

## Affected
- Maven: `org.mortbay.jetty:jetty` — affected >=0 <4.2.19

## Details
HttpRequest.java in Jetty HTTP Server before 4.2.19 allows remote attackers to cause denial of service (memory usage and application crash) via HTTP requests with a large Content-Length.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2004-2381
- https://exchange.xforce.ibmcloud.com/vulnerabilities/15537
- http://cvs.sourceforge.net/viewcvs.py/jetty/Jetty/src/org/mortbay/http/HttpRequest.java?r1=1.75&r2=1.76
- http://sourceforge.net/project/shownotes.php?release_id=224743
- http://www.osvdb.org/4387
