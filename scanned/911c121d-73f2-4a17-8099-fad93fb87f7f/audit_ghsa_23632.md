# [M] Apache Ambari Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-w3p6-94x2-xcvm
CVE: CVE-2015-5210
CWE: CWE-601
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-w3p6-94x2-xcvm
Type: github-advisory

## Affected
- Maven: `org.apache.ambari:ambari` — affected >=1.7.0 <2.1.2

## Details
Open redirect vulnerability in Apache Ambari before 2.1.2 allows remote attackers to redirect users to arbitrary web sites and conduct phishing attacks via a URL in the targetURI parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5210
- https://cwiki.apache.org/confluence/display/AMBARI/Ambari+Vulnerabilities#AmbariVulnerabilities-FixedinAmbari2.1.2
- http://www.openwall.com/lists/oss-security/2015/10/13/4
