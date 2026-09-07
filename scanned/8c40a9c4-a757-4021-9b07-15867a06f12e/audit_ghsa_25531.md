# [M] Liferay Portal and Liferay DXP allows arbitrary injection via web content template names

## Summary
Severity: Medium
Advisory: GHSA-w7f2-6896-6mm2
CVE: CVE-2022-26596
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-26
Source: https://github.com/advisories/GHSA-w7f2-6896-6mm2
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.journal.content.web` — affected >=0 <5.0.15
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.0.0 <7.0.10.fp94
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp8

## Details
Cross-site scripting (XSS) vulnerability in Journal module's web content display configuration page before 5.0.15 in Liferay Portal 7.1.0 through 7.3.3, and Liferay DXP 7.0 before fix pack 94, 7.1 before fix pack 19, and 7.2 before fix pack 8, allows remote attackers to inject arbitrary web script or HTML via web content template names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26596
- https://github.com/liferay/liferay-portal/commit/c61976fc867f3add8eb429b99380e91f021f9313
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2022-26596-stored-xss-with-template-name?p_r_p_assetEntryId=121612108&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D121612108%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
- http://liferay.com
