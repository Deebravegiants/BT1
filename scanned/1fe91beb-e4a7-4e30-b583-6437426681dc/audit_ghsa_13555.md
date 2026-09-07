# [C] Liferay Portal and Liferay DXP Vulnerable to Reflected XSS via the Export for Translation Page

## Summary
Severity: Critical
Advisory: GHSA-w2g3-j73q-7qv7
CVE: CVE-2023-42497
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-w2g3-j73q-7qv7
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.translation.web` — affected >=0 <2.0.86
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.0 <7.4.13.u86

## Details
Reflected cross-site scripting (XSS) vulnerability on the Export for Translation page before 2.0.86 from Liferay Portal (7.4.3.4 through 7.4.3.85), and Liferay DXP 7.4 before update 86 allows remote attackers to inject arbitrary web script or HTML via the `_com_liferay_translation_web_internal_portlet_TranslationPortlet_redirect` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-42497
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2023-42497?p_r_p_assetEntryId=122124913&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D122124913%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
