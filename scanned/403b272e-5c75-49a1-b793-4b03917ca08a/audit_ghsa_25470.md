# [H] Mule modules contain Directory Traversal

## Summary
Severity: High
Advisory: GHSA-mwh9-gr45-xvv4
CVE: CVE-2019-15630
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mwh9-gr45-xvv4
Type: github-advisory

## Affected
- Maven: `org.mule.runtime:mule` — affected >=3.0.0

## Details
Directory Traversal in APIkit, http-connector, and OAuth2 Provider modules in Mulesoft 3.x, 4.x and Mulesoft API Gateway (all versions) released before August 1, 2019 allow remote attackers to read files accessible to the Mule process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15630
- https://github.com/mulesoft/mule
- https://help.mulesoft.com/s/article/Directory-traversal-vulnerability-affecting-runtimes-of-MuleSoft-customers-running-certain-use-cases-of-Mule-flows-and-API-Gateways
