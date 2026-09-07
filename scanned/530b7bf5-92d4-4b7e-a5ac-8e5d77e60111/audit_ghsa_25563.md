# [M] Liferay Portal and Liferay DXP allows arbitrary injection via the site name

## Summary
Severity: Medium
Advisory: GHSA-3vww-jrmm-9vff
CVE: CVE-2022-26597
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-26
Source: https://github.com/advisories/GHSA-3vww-jrmm-9vff
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.layout.seo.web` — affected >=0 <2.0.4
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.fp3

## Details
Cross-site scripting (XSS) vulnerability in the Layout module's Open Graph integration before 2.0.4 in Liferay Portal 7.3.0 through 7.4.0, and Liferay DXP 7.3 before service pack 3 allows remote attackers to inject arbitrary web script or HTML via the site name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26597
- https://github.com/liferay/liferay-portal/commit/fd7fc6e186b36944b045e0fdf368e588889c3f02
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17282
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2022-26597-stored-xss-with-site-name-in-open-graph-integration?p_r_p_assetEntryId=121612214&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D121612214%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
