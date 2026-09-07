# [M] WSO2 Registry Stored Cross Site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rfq3-wpjh-ppvg
CVE: CVE-2023-6911
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-22
Source: https://github.com/advisories/GHSA-rfq3-wpjh-ppvg
Type: github-advisory

## Affected
- Maven: `org.wso2.carbon.registry:carbon-registry` — affected >=0 <4.7.37

## Details
WSO2 Registry has been identified as vulnerable due to improper output encoding, a Stored Cross Site Scripting (XSS) attack can be carried out by an attacker injecting a malicious payload into the Registry feature of the Management Console.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6911
- https://github.com/wso2/carbon-registry/commit/878fc7e53c90acc85e303d2af73440014a68b246
- https://github.com/wso2/carbon-registry
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2021/WSO2-2020-1225
