# [M] Apache Geronimo Application Server multiple cross-site scripting (XSS) vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-c372-x57p-6x7v
CVE: CVE-2009-0038
CWE: CWE-79
Ecosystem: Maven
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-c372-x57p-6x7v
Type: github-advisory

## Affected
- Maven: `org.apache.geronimo.plugins:console` — affected >=2.1.0 <2.1.4

## Details
Multiple cross-site scripting (XSS) vulnerabilities in the web administration console in Apache Geronimo Application Server 2.1 through 2.1.3 allow remote attackers to inject arbitrary web script or HTML via the (1) name, (2) ip, (3) username, or (4) description parameter to console/portal/Server/Monitoring; or (5) the PATH_INFO to the default URI under console/portal/.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-0038
- https://github.com/apache/geronimo/commit/aa0c2c26dde8930cad924796af7c17a13d236b16
- https://github.com/apache/geronimo
- https://web.archive.org/web/20090419162753/http://secunia.com/advisories/34715
- https://web.archive.org/web/20090422192202/http://dsecrg.com/pages/vul/show.php?id=119
- https://web.archive.org/web/20200229223125/http://www.securityfocus.com/bid/34562
- http://geronimo.apache.org/21x-security-report.html#2.1.xSecurityReport-214
- http://issues.apache.org/jira/browse/GERONIMO-4597
