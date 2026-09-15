# [M] WSO2 Identity Server Apps allows content spoofing in logs

## Summary
Severity: Medium
Advisory: GHSA-r6f3-55wj-g9p3
CVE: CVE-2024-6429
CWE: CWE-451
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-09-23
Source: https://github.com/advisories/GHSA-r6f3-55wj-g9p3
Type: github-advisory

## Affected
- Maven: `org.wso2.identity.apps:authentication-portal` — affected >=0 <2.4.4

## Details
A content spoofing issue exists in WSO2 Identity Server Apps, specifically in the Authentication Portal, due to improper handling of authentication error messages. When an authentication failure occurs, the portal previously accepted an `authFailureMsg` value supplied via URL and rendered it in the UI without validating it against the resource bundle. An attacker can craft a link that causes the portal to display attacker-controlled text in the error banner, enabling UI misrepresentation and social-engineering.

The fix validates the message key against the resource bundle and encodes input before rendering. Upgrade to `org.wso2.identity.apps:authentication-portal` **2.4.4** or later to remediate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6429
- https://github.com/wso2/identity-apps/pull/6488
- https://github.com/wso2/identity-apps/commit/75babf6b60f940f86bada7020e5d464ca95e47f2
- https://github.com/wso2/identity-apps
- https://github.com/wso2/identity-apps/releases/tag/@wso2is/identity-apps-core@2.4.4
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2025/WSO2-2024-3490
