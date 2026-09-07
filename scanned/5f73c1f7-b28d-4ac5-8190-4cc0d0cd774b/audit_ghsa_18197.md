# [M] Liferay Portal's System, Instance and Site Settings are vulnerable to Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-m55r-9fx8-725j
CVE: CVE-2025-43795
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-12
Source: https://github.com/advisories/GHSA-m55r-9fx8-725j
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.configuration.admin.web` — affected >=2.0.7 <5.0.76
- Maven: `com.liferay:com.liferay.site.admin.web` — affected >=2.0.4 <5.0.103

## Details
An open redirect vulnerability in the System Settings in Liferay Portal 7.1.0 through 7.4.3.101, and Liferay DXP 2023.Q3.1 through 2023.Q3.4 , 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions allows remote attackers to redirect users to arbitrary external URLs via the _com_liferay_configuration_admin_web_portlet_SystemSettingsPortlet_redirect parameter.

An open redirect vulnerability in the Instance Settings in Liferay Portal 7.1.0 through 7.4.3.101, and Liferay DXP 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions allows remote attackers to redirect users to arbitrary external URLs via the _com_liferay_configuration_admin_web_portlet_InstanceSettingsPortlet_redirect parameter.

An open redirect vulnerability in the Site Settings in Liferay Portal 7.1.0 through 7.4.3.101, and Liferay DXP 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions allows remote attackers to redirect users to arbitrary external URLs via the _com_liferay_site_admin_web_portlet_SiteSettingsPortlet_redirect parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43795
- https://github.com/liferay/liferay-portal/commit/81b2bdf2f48dbd467718ccc95c5bba31e5985fab
- https://github.com/liferay/liferay-portal/commit/cf23864f2b7a0e346f42961e0ad6c7ef5facb2b4
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43795
