# [M] CVE-2025-43792

## Summary
Severity: Medium
Advisory: CVE-2025-43792
Aliases: GHSA-vp64-77c6-33h8
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2025-43792
Type: osv

## Details
Remote staging in Liferay Portal 7.4.0 through 7.4.3.105, and older unsupported versions, and Liferay DXP 2023.Q4.0, 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions does not properly obtain the remote address of the live site from the database which, which allows remote authenticated users to exfiltrate data to an attacker controlled server (i.e., a fake “live site”) via the _com_liferay_exportimport_web_portlet_ExportImportPortlet_remoteAddress and _com_liferay_exportimport_web_portlet_ExportImportPortlet_remotePort parameters. To successfully exploit this vulnerability, an attacker must also successfully obtain the staging server’s shared secret and add the attacker controlled server to the staging server’s whitelist.

## References
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43792
