# [M] WSO2 incorrect authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6qjp-wm6g-m32r
CVE: CVE-2024-2321
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-02-27
Source: https://github.com/advisories/GHSA-6qjp-wm6g-m32r
Type: github-advisory

## Affected
- Maven: `org.wso2.am:am-parent` — affected >=4.2.0-beta
- Maven: `org.wso2.am:am-parent` — affected >=4.1.0-alpha
- Maven: `org.wso2.am:am-parent` — affected >=4.0.0-beta
- Maven: `org.wso2.is:identity-server-parent` — affected >=6.1.0-beta
- Maven: `org.wso2.is:identity-server-parent` — affected >=6.0.0-alpha3
- Maven: `org.wso2.is:identity-server-parent` — affected >=5.11.0-alpha

## Details
An incorrect authorization vulnerability exists in multiple WSO2 products, allowing protected APIs to be accessed directly using a refresh token instead of the expected access token. Due to improper authorization checks and token mapping, session cookies are not required for API access, potentially enabling unauthorized operations.

Exploitation requires an attacker to obtain a valid refresh token of an admin user. Since refresh tokens generally have a longer expiration time, this could lead to prolonged unauthorized access to API resources, impacting data confidentiality and integrity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2321
- https://github.com/wso2/docs-security/blob/76bad9a2f38dc3377af476d0be52c6e775e3d864/en/docs/security-announcements/security-advisories/2024/WSO2-2024-3213.md
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2024/WSO2-2024-3213
