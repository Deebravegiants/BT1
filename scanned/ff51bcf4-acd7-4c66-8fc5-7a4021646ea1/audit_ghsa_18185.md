# [M] Liferay has Insecure Default Initialization of Resource issue

## Summary
Severity: Medium
Advisory: GHSA-25m3-w28p-v3v3
CVE: CVE-2025-43797
CWE: CWE-1188
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-16
Source: https://github.com/advisories/GHSA-25m3-w28p-v3v3
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.site.admin.web` — affected >=0 <5.0.111

## Details
In Liferay Portal 7.1.0 through 7.4.3.111, and Liferay DXP 2023.Q4.0, 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions, the default membership type of a newly created site is “Open” which allows any registered users to become a member of the site. A remote attacker with site membership can potentially view, add or edit content on the site.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43797
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43797
