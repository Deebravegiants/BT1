# [M] Liferay Portal cross-site scripting (XSS) vulnerability in the Frontend Taglib module

## Summary
Severity: Medium
Advisory: GHSA-9h7f-5hc8-cj5f
CVE: CVE-2021-35463
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9h7f-5hc8-cj5f
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0 <7.4.1
- Maven: `com.liferay:com.liferay.frontend.taglib.clay` — affected >=0 <7.1.15

## Details
Cross-site scripting (XSS) vulnerability in the Frontend Taglib module in Liferay Portal 7.4.0 allows remote attackers to inject arbitrary web script or HTML into the management toolbar search via the `keywords` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-35463
- https://github.com/liferay/liferay-portal/commit/751a70e0ed7b380ea2ab510ff79ddb33ed87dd9b
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2021-35463-reflected-xss-with-keywords-in-search?p_r_p_assetEntryId=121611661&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D121611661%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
