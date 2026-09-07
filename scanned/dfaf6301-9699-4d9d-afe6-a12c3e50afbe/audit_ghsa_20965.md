# [M] Liferay Portal and Liferay DXP Vulnerable to XSS via Tag Name

## Summary
Severity: Medium
Advisory: GHSA-wffm-j7m8-93g4
CVE: CVE-2022-28982
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-23
Source: https://github.com/advisories/GHSA-wffm-j7m8-93g4
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.asset.taglib` — affected >=0 <6.1.9

## Details
A cross-site scripting (XSS) vulnerability in Liferay Asset Taglib before v6.1.9 from Liferay Portal (v7.3.3 through v7.4.2) and Liferay DXP v7.3 before service pack 3 allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into the name of a tag.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28982
- https://github.com/liferay/liferay-portal/commit/ae71b53861313c6e1c5ac02e129239ea413e0488
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17363
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2022-28982-reflected-xss-with-tag-name-in-liferay-asset-asset-tags-selector-?p_r_p_assetEntryId=121612466&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D121612466%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
- https://web.archive.org/web/20220922060111/https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-28982-reflected-xss-with-tag-name-in-%3Cliferay-asset-asset-tags-selector%3E
- http://liferay.com
