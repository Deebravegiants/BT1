# [H] Liferay Portal Path Traversal Vulnerability via the Hypermedia REST APIs Module

## Summary
Severity: High
Advisory: GHSA-5j86-vmpx-42pc
CVE: CVE-2022-28981
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-23
Source: https://github.com/advisories/GHSA-5j86-vmpx-42pc
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.headless.discovery.web` — affected >=0 <4.0.12

## Details
Path traversal vulnerability in the Hypermedia REST APIs module before 4.0.12 from Liferay Portal (7.4.0 through 7.4.2) allows remote attackers to access files outside of com.liferay.headless.discovery.web/META-INF/resources via the `parameter` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28981
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2022-28981-path-traversal-vulnerability-in-hypermedia-rest-apis?p_r_p_assetEntryId=121612450&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D121612450%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
- https://web.archive.org/web/20220929232244/https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-28981-path-traversal-vulnerability-in-hypermedia-rest-apis
- http://liferay.com
