# [M] Apache Geronimo Application Server CSRF vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-678x-xfp4-r92r
CVE: CVE-2009-0039
CWE: CWE-352
Ecosystem: Maven
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-678x-xfp4-r92r
Type: github-advisory

## Affected
- Maven: `org.apache.geronimo.plugins:console` — affected >=0 <2.1.4

## Details
Multiple cross-site request forgery (CSRF) vulnerabilities in the web administration console in Apache Geronimo Application Server 2.1 through 2.1.3 allow remote attackers to hijack the authentication of administrators for requests that (1) change the web administration password, (2) upload applications, and perform unspecified other administrative actions, as demonstrated by (3) a Shutdown request to console/portal//Server/Shutdown.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-0039
- https://github.com/apache/geronimo/commit/aa0c2c26dde8930cad924796af7c17a13d236b16
- https://svn.apache.org/viewvc/geronimo/server
- http://dsecrg.com/pages/vul/show.php?id=120
- http://geronimo.apache.org/21x-security-report.html#2.1.xSecurityReport-214
- http://issues.apache.org/jira/browse/GERONIMO-4597
- http://secunia.com/advisories/34715
- http://www.securityfocus.com/archive/1/502735/100/0/threaded
- http://www.securityfocus.com/bid/34562
- http://www.vupen.com/english/advisories/2009/1089
