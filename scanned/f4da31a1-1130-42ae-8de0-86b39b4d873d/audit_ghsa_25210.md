# [H] Apache Geronimo Application Server multiple directory traversal vulnerabilities

## Summary
Severity: High
Advisory: GHSA-xm92-rf24-h74w
CVE: CVE-2008-5518
CWE: CWE-22
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xm92-rf24-h74w
Type: github-advisory

## Affected
- Maven: `org.apache.geronimo.plugins:console` — affected >=2.1.0 <2.1.4

## Details
Multiple directory traversal vulnerabilities in the web administration console in Apache Geronimo Application Server 2.1 through 2.1.3 on Windows allow remote attackers to upload files to arbitrary directories via directory traversal sequences in the (1) group, (2) artifact, (3) version, or (4) fileType parameter to console/portal//Services/Repository (aka the Services/Repository portlet); the (5) createDB parameter to console/portal/Embedded DB/DB Manager (aka the Embedded DB/DB Manager portlet); or the (6) filename parameter to the createKeystore script in the Security/Keystores portlet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-5518
- https://github.com/apache/geronimo/commit/aa0c2c26dde8930cad924796af7c17a13d236b16
- https://exchange.xforce.ibmcloud.com/vulnerabilities/49898
- https://exchange.xforce.ibmcloud.com/vulnerabilities/49899
- https://exchange.xforce.ibmcloud.com/vulnerabilities/49900
- https://github.com/apache/geronimo
- https://web.archive.org/web/20090419162753/http://secunia.com/advisories/34715
- https://web.archive.org/web/20090422192030/http://dsecrg.com/pages/vul/show.php?id=118
- https://web.archive.org/web/20200229223125/http://www.securityfocus.com/bid/34562
- https://www.exploit-db.com/exploits/8458
- http://geronimo.apache.org/21x-security-report.html#2.1.xSecurityReport-214
- http://issues.apache.org/jira/browse/GERONIMO-4597
