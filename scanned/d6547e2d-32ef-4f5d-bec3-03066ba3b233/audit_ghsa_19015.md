# [M] WSO2 Carbon Mediation vulnerable to XML External Entity (XXE) attacks

## Summary
Severity: Medium
Advisory: GHSA-fvfq-q238-j7j3
CVE: CVE-2025-10713
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2025-11-05
Source: https://github.com/advisories/GHSA-fvfq-q238-j7j3
Type: github-advisory

## Affected
- Maven: `org.wso2.carbon.mediation:org.wso2.carbon.localentry` — affected >=0

## Details
An XML External Entity (XXE) vulnerability exists in multiple WSO2 products due to improper configuration of the XML parser. The application parses user-supplied XML without applying sufficient restrictions, allowing resolution of external entities.

A successful attack could enable a remote, unauthenticated attacker to read sensitive files from the server's filesystem or perform denial-of-service (DoS) attacks that render affected services unavailable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10713
- https://github.com/wso2/carbon-mediation/pull/1784
- https://github.com/wso2/carbon-mediation/commit/b995b2f1db96a4697791f0202cc8713f15640fd5
- https://github.com/wso2/carbon-mediation
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2025/WSO2-2025-4505
