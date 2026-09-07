# [M] Liferay Portal Insecure Default Configuration in auth.login.prompt.enabled

## Summary
Severity: Medium
Advisory: GHSA-9427-7f65-88c8
CVE: CVE-2022-41414
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-07
Source: https://github.com/advisories/GHSA-9427-7f65-88c8
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.0.0-a1 <7.4.2-ga3
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <8.0.0

## Details
An insecure default in the component auth.login.prompt.enabled of Liferay Portal v7.0.0 through v7.4.2 allows attackers to enumerate usernames, site names, and pages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41414
- https://github.com/liferay/liferay-portal/commit/659c4422bd32b1db1a01a7f4a42b7702d512ffa2
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2022-01-insecure-defaults-auth-login-prompt-enabled?p_r_p_assetEntryId=121612026&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D121612026%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
