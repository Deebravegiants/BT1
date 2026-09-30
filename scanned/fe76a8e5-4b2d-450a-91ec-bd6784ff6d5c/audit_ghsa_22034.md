# [H] Liferay Portal and Liferay DXP fails to invalidate password reset tokens after use

## Summary
Severity: High
Advisory: GHSA-vwj8-4grf-3r8v
CVE: CVE-2021-33322
CWE: CWE-613
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vwj8-4grf-3r8v
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <5.7.3
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.0.0 <7.0.10.fp96
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp18
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp5

## Details
In implementation for the portal services before 5.7.3 in Liferay Portal 7.3.0 and earlier, and Liferay DXP 7.0 before fix pack 96, 7.1 before fix pack 18, and 7.2 before fix pack 5, password reset tokens are not invalidated after a user changes their password, which allows remote attackers to change the user’s password via the old password reset token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33322
- https://github.com/liferay/liferay-portal/commit/8f072ee8527a1dd5c0ffa91c4a78641d0e666b95
- https://github.com/liferay/liferay-portal/commit/9fe453b34f58286a504d995be8ba50499adcf1b7
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-16981
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2021-33322-password-change-does-not-invalidate-password-reset-tokens?p_r_p_assetEntryId=121610648&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D121610648%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
