# [M] Apache Ambari SSRF Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9g2j-5685-h44h
CVE: CVE-2015-1775
CWE: CWE-918
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9g2j-5685-h44h
Type: github-advisory

## Affected
- Maven: `org.apache.ambari:ambari` — affected >=1.5.0 <2.1.0

## Details
Server-side request forgery (SSRF) vulnerability in the proxy endpoint (`api/v1/proxy`) in Apache Ambari before 2.1.0 allows remote authenticated users to conduct port scans and access unsecured services via a crafted REST call.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1775
- https://cwiki.apache.org/confluence/display/AMBARI/Ambari+Vulnerabilities#AmbariVulnerabilities-FixedinAmbari2.1.0
- http://www.openwall.com/lists/oss-security/2015/10/13/2
