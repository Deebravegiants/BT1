# [M] WSO2 products vulnerable to privilege escalation due to business logic flaw in SOAP admin services

## Summary
Severity: Medium
Advisory: GHSA-j63j-7r7r-5v4j
CVE: CVE-2024-7096
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-05-30
Source: https://github.com/advisories/GHSA-j63j-7r7r-5v4j
Type: github-advisory

## Affected
- Maven: `org.wso2.am:am-parent` — affected >=2.0.0 <4.4.0
- Maven: `org.wso2.is:identity-server-parent` — affected >=5.2.0 <7.1.0

## Details
A privilege escalation vulnerability exists in multiple WSO2 products due to a business logic flaw in SOAP admin services. A malicious actor can create a new user with elevated permissions only when all of the following conditions are met:
  *  SOAP admin services are accessible to the attacker.
  *  The deployment includes an internally used attribute that is not part of the default WSO2 product configuration.
  *  At least one custom role exists with non-default permissions.
  *  The attacker has knowledge of the custom role and the internal attribute used in the deployment.


Exploiting this vulnerability allows malicious actors to assign higher privileges to self-registered users, bypassing intended access control mechanisms.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7096
- https://github.com/wso2/docs-security/blob/cfd53689909eef62fc5427e193e35e7df8ab1ef8/en/docs/security-announcements/security-advisories/2024/WSO2-2024-3573.md
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2024/WSO2-2024-3573
