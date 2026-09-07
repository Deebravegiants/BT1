# [M] Liferay Portal vulnerable to cross-site scripting (XSS) via the keywords parameter

## Summary
Severity: Medium
Advisory: GHSA-9536-m86r-q297
CVE: CVE-2021-38264
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-04
Source: https://github.com/advisories/GHSA-9536-m86r-q297
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.frontend.taglib.clay` — affected >=0 <7.1.15

## Details
Liferay Portal v7.4.1 and below was discovered to contain a cross-site scripting (XSS) vulnerability via the keywords parameter under the Frontend Taglib module before 7.1.15.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38264
- https://github.com/liferay/liferay-portal/commit/f5df5cbfdc8254b2388fa445e62ec1efebe3547f
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2021-38264-reflected-xss-with-keywords-in-search?p_r_p_assetEntryId=121611971&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D121611971%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
