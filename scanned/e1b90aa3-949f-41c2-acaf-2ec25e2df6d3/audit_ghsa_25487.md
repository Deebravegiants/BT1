# [M] Liferay Portal and Liferay DXP allows arbitrary injection via form field

## Summary
Severity: Medium
Advisory: GHSA-658f-xhv4-p978
CVE: CVE-2022-26594
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-16
Source: https://github.com/advisories/GHSA-658f-xhv4-p978
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.dynamic.data.mapping.form.field.type` — affected >=0 <6.0.11
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.fp3

## Details
Multiple cross-site scripting (XSS) vulnerabilities in Dynamic Data Mapping Form Field Type before 6.0.11 from Liferay Portal 7.3.5 through 7.4.0, and Liferay DXP 7.3 before service pack 3 allow remote attackers to inject arbitrary web script or HTML via a form field's help text to (1) Forms module's form builder, or (2) App Builder module's object form view's form builder.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26594
- https://github.com/liferay/liferay-portal/commit/7c9348cc59271647cfd192c007d383d80ae9a667
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17290
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2022-26594-xss-vulnerability-with-form-field-help-text?p_r_p_assetEntryId=121612173&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect=https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities%3Fp_p_id%3Dcom_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt%26p_p_lifecycle%3D0%26p_p_state%3Dnormal%26p_p_mode%3Dview%26p_r_p_assetEntryId%3D121612173%26_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_cur%3D0%26p_r_p_resetCur%3Dfalse
