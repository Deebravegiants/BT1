# [H] Multiple WSO2 products vulnerable to perform user impersonatoin using JIT provisioning

## Summary
Severity: High
Advisory: GHSA-f6jm-9pr8-9c3w
CVE: CVE-2023-6837
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2023-12-15
Source: https://github.com/advisories/GHSA-f6jm-9pr8-9c3w
Type: github-advisory

## Affected
- Maven: `org.wso2.carbon.identity.framework:org.wso2.carbon.identity.application.authentication.framework` — affected >=0 <5.20.254
- Maven: `org.wso2.identity.apps:authentication-portal` — affected >=0 <1.6.179.1

## Details
Multiple WSO2 products have been identified as vulnerable to perform user impersonatoin using JIT provisioning. In order for this vulnerability to have any impact on your deployment, following conditions must be met:

  *  An IDP configured for federated authentication and JIT provisioning enabled with the "Prompt for username, password and consent" option.
  *  A service provider that uses the above IDP for federated authentication and has the "Assert identity using mapped local subject identifier" flag enabled.


Attacker should have:

  *  A fresh valid user account in the federated IDP that has not been used earlier.
  *  Knowledge of the username of a valid user in the local IDP.


When all preconditions are met, a malicious actor could use JIT provisioning flow to perform user impersonation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6837
- https://github.com/wso2/carbon-identity-framework/commit/fdab609760784086b8a3f55f7acf46d977a03d79
- https://github.com/wso2/identity-apps/commit/1424203bbe81688d661ea8b8cd28e332302e1c53
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2022/WSO2-2021-1573
