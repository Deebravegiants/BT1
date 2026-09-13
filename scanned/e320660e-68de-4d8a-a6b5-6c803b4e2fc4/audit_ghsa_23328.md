# [C] Mulesoft Mule Unsafe Deserialization

## Summary
Severity: Critical
Advisory: GHSA-cvcf-w75c-gw5r
CVE: CVE-2019-13116
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cvcf-w75c-gw5r
Type: github-advisory

## Affected
- Maven: `org.mule.runtime:mule` — affected >=0 <3.8.0

## Details
The MuleSoft Mule runtime engine before 3.8.0 allows remote attackers to execute arbitrary code because of Java Deserialization, related to Apache Commons Collections.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13116
- https://docs.mulesoft.com/release-notes/mule-runtime/mule-3.8.0-release-notes
- https://github.com/mulesoft/mule
- https://threat.tevora.com/mulesoft-3-8-unauthenticated-rce
