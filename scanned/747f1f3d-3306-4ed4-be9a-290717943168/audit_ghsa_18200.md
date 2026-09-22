# [M] Liferay Portal and DXP does not properly expire sessions

## Summary
Severity: Medium
Advisory: GHSA-rpx3-f938-xj5q
CVE: CVE-2025-43819
CWE: CWE-613
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-rpx3-f938-xj5q
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.saml.impl` — affected >=0 <5.0.51

## Details
### Summary

Liferay Portal/DXP contains an Insufficient Session Expiration issue where the Single Logout (SLO) API may fail to invalidate a user’s previous session. An attacker can reuse a stale session via the SLO endpoint to gain an authenticated context.

### Affected Versions

The following platform versions are affected:

*   **Liferay Portal:**  
    *   `7.3.3.131` through `7.4.3.121`
*   **Liferay DXP:**
    *   `2024.Q4.0`–`2024.Q4.3`
    *   `2024.Q3.1`–`2024.Q3.13`
    *   `2024.Q2.0`–`2024.Q2.13`
    *   `2024.Q1.1`–`2024.Q1.12`

### Remediation

Update to the fixed builds and, for Maven consumers of the SAML module, upgrade `com.liferay:com.liferay.saml.impl` to **5.0.51** or later. After upgrading, ensure session invalidation policies are enforced and verify SLO behavior end-to-end.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43819
- https://github.com/liferay/liferay-portal/commit/433dff5edae4414fdc436b49a9edb62d721c84b5
- https://github.com/liferay/liferay-portal/commit/da9105a61d788801797797a32583a4b76c902cdc
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18159
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43819
- https://osv.dev/vulnerability/GHSA-rpx3-f938-xj5q
