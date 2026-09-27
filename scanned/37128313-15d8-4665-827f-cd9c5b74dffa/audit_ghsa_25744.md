# [M] Liferay Portal and Liferay DXP fails to check origin of event messages

## Summary
Severity: Medium
Advisory: GHSA-ghw5-998m-vw4w
CVE: CVE-2022-25146
CWE: CWE-346
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-03-04
Source: https://github.com/advisories/GHSA-ghw5-998m-vw4w
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.remote.app.web` — affected >=0 <2.0.21
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.4.13.u5

## Details
The Remote App module before 2.0.21 from Liferay Portal v7.4.3.4 through v7.4.3.8 and Liferay DXP 7.4 before update 5 does not check if the origin of event messages it receives matches the origin of the Remote App, allowing attackers to exfiltrate the CSRF token via a crafted event message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25146
- https://github.com/liferay/liferay-portal/commit/2fe144127a1a3b4c74f47e4b760b992b997c276b
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2022-25146-csrf-token-exfiltration-via-remote-apps?p_r_p_assetEntryId=121612000&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D121612000%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-25146-csrf-token-exfiltration-via-remote-apps
- http://liferay.com
