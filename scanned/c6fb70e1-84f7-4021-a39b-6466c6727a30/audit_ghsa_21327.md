# [M] Liferay Portal Vulnerable to XSS in the Object Module

## Summary
Severity: Medium
Advisory: GHSA-x43w-xphx-86w3
CVE: CVE-2022-42115
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-x43w-xphx-86w3
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.object.web` — affected >=0 <1.0.99

## Details
Cross-site scripting (XSS) vulnerability in the Object module's edit object details page in Liferay Object Web before 1.0.99 from Liferay Portal (7.4.3.4 through 7.4.3.36) allows remote attackers to inject arbitrary web script or HTML via a crafted payload injected into the object field's `Label` text field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42115
- https://github.com/liferay/liferay-portal/commit/51cc09f972c1ffb7186680b3b73f463406daae46
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17613
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2022-42115?p_r_p_assetEntryId=121613168&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D121613168%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
- https://web.archive.org/web/20221019053234/https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-42115
- http://liferay.com
