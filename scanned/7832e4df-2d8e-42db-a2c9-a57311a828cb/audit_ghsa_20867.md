# [M] Liferay Portal and Liferay DXP Vulnerable to XSS via the filter_ Prefix

## Summary
Severity: Medium
Advisory: GHSA-8mp9-w7gr-pvj3
CVE: CVE-2022-28980
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-23
Source: https://github.com/advisories/GHSA-8mp9-w7gr-pvj3
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.fragment.renderer.collection.filter.impl` — affected >=0 <1.0.11
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.4.3.5-ga5

## Details
Multiple cross-site scripting (XSS) vulnerabilities in Liferay Fragment Renderer Collection Filter Implementation before v1.0.11 from Liferay Portal (v7.4.3.4) and Liferay DXP v7.4 GA allows attackers to execute arbitrary web scripts or HTML via parameters with the filter_ prefix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28980
- https://github.com/liferay/liferay-portal/commit/b4ea3e9acb6c3602b9c90538ba35f11906dc07ed
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17420
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2022-28980-reflected-xss-with-filter_-parameters-in-applied-fragment-filters?p_r_p_assetEntryId=121612438&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D121612438%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
- https://web.archive.org/web/20221114081624/https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-28980-reflected-xss-with-filter_*-parameters-in-applied-fragment-filters
- http://liferay.com
