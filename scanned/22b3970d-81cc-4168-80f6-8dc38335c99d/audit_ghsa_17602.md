# [H] Liferay Portal path traversal vulnerability with the downloading and installation of Xuggler

## Summary
Severity: High
Advisory: GHSA-p73j-gpcq-49h8
CVE: CVE-2025-3594
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-16
Source: https://github.com/advisories/GHSA-p73j-gpcq-49h8
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.server.admin.web` — affected >=5.0.0 <5.0.24
- Maven: `com.liferay:com.liferay.server.admin.web` — affected >=4.0.0 <4.0.48
- Maven: `com.liferay:com.liferay.server.admin.web` — affected >=3.0.0 <3.0.67
- Maven: `com.liferay:com.liferay.server.admin.web` — affected >=2.0.0 <2.0.66
- Maven: `com.liferay:com.liferay.server.admin.web` — affected >=0 <1.0.93

## Details
Path traversal vulnerability with the downloading and installation of Xuggler in Liferay Portal 7.0.0 through 7.4.3.4, and Liferay DXP 7.4 GA, 7.3 GA through update 34, and older unsupported versions allows remote attackers to (1) add files to arbitrary locations on the server and (2) download and execute arbitrary files from the download server via the `_com_liferay_server_admin_web_portlet_ServerAdminPortlet_jarName` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3594
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-3594
