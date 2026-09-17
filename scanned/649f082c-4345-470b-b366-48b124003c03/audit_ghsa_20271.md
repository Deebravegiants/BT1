# [C] XML External Entity Reference in drools

## Summary
Severity: Critical
Advisory: GHSA-rc57-9r3x-98cq
CVE: CVE-2021-41411
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-rc57-9r3x-98cq
Type: github-advisory

## Affected
- Maven: `org.drools:drools-core` — affected >=0 <7.60.0.Final

## Details
drools <=7.59.x is affected by an XML External Entity (XXE) vulnerability in KieModuleMarshaller.java. The Validator class is not used correctly, resulting in the XXE injection vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41411
- https://github.com/apache/incubator-kie-drools/pull/3808
- https://github.com/kiegroup/drools
