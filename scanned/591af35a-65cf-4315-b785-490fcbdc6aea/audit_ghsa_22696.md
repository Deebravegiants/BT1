# [M] Liferay Portal and Liferay DXP vulnerable to email spam via lack of flagging rate

## Summary
Severity: Medium
Advisory: GHSA-wg4x-hf94-fj5v
CVE: CVE-2021-33320
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wg4x-hf94-fj5v
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.flags.taglib` — affected >=0 <5.0.11
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.0.0 <7.0.10.fp96
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp20
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp5

## Details
The Flags module before version 5.0.11 in Liferay Portal 7.3.1 and earlier, and Liferay DXP 7.0 before fix pack 96, 7.1 before fix pack 20, and 7.2 before fix pack 5, does not limit the rate at which content can be flagged as inappropriate, which allows remote authenticated users to spam the site administrator with emails

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33320
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17007
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2021-33320-flagging-content-as-inappropriate-is-not-rate-limited?p_r_p_assetEntryId=121611464&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D121611464%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
