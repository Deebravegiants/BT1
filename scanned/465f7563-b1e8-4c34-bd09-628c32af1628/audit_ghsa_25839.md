# [M] Liferay Portal and Liferay DXP vulnerable to cross-site scripting (XSS) in the Gogo Shell module

## Summary
Severity: Medium
Advisory: GHSA-vw6g-gh6c-8qwp
CVE: CVE-2021-38269
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-04
Source: https://github.com/advisories/GHSA-vw6g-gh6c-8qwp
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.gogo.shell.web` — affected >=0 <5.0.2
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp23
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp13
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.fp2

## Details
Cross-site scripting (XSS) vulnerability in the Gogo Shell module before 5.0.2 from Liferay Portal 7.1.0 through 7.3.6 and 7.4.0, and Liferay DXP 7.1 before fix pack 23, 7.2 before fix pack 13, and 7.3 before fix pack 2 allows remote attackers to inject arbitrary web script or HTML via the output of a Gogo Shell command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38269
- https://github.com/liferay/liferay-portal/commit/0b28a0d0ca7592660c66c15aa14fe709b7c0c141
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17203
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2021-38269-stored-xss-with-gogo-shell-output?p_r_p_assetEntryId=121611883&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D121611883%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
