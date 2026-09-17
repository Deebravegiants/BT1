# [M] Improper Authentication in Apache Axis2

## Summary
Severity: Medium
Advisory: GHSA-66rx-gqx3-p98m
CVE: CVE-2012-5351
CWE: CWE-287
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-66rx-gqx3-p98m
Type: github-advisory

## Affected
- Maven: `org.apache.axis2:axis2` — affected >=0 <1.6.4

## Details
Apache Axis2 allows remote attackers to forge messages and bypass authentication via a SAML assertion that lacks a Signature element, aka a "Signature exclusion attack," a different vulnerability than CVE-2012-4418.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5351
- https://exchange.xforce.ibmcloud.com/vulnerabilities/79487
- https://www.oracle.com/security-alerts/cpuapr2022.html
- http://www.nds.rub.de/media/nds/veroeffentlichungen/2012/08/22/BreakingSAML_3.pdf
