# [M] WSO2 is vulnerable to Open Redirect through multi-option URL in its authentication endpoint

## Summary
Severity: Medium
Advisory: GHSA-cp5v-2hmc-3vjx
CVE: CVE-2024-1440
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-06-02
Source: https://github.com/advisories/GHSA-cp5v-2hmc-3vjx
Type: github-advisory

## Affected
- Maven: `org.wso2.carbon.identity.framework:org.wso2.carbon.identity.application.authentication.endpoint.util` — affected >=6.0.0 <7.0.111
- Maven: `org.wso2.carbon.identity.framework:org.wso2.carbon.identity.application.authentication.endpoint.util` — affected >=0 <5.25.707

## Details
An open redirection vulnerability exists in multiple WSO2 products due to improper validation of the multi-option URL in the authentication endpoint when multi-option authentication is enabled. A malicious actor can craft a valid link that redirects users to an attacker-controlled site.

By exploiting this vulnerability, an attacker may trick users into visiting a malicious page, enabling phishing attacks to harvest sensitive information or perform other harmful actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1440
- https://github.com/wso2/carbon-identity-framework/pull/5580
- https://github.com/wso2/carbon-identity-framework/pull/5747
- https://github.com/wso2/carbon-identity-framework/commit/29ea34ada98649c4ae71aa92f1cbe87ce82164b9
- https://github.com/wso2/carbon-identity-framework/commit/7033924b6d53ff843529743b259f6c48f4e9c177
- https://github.com/wso2/carbon-identity-framework
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2024/WSO2-2024-3171
