# [M] Liferay Stored Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vg6h-g5mr-9hgv
CVE: CVE-2025-43802
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-16
Source: https://github.com/advisories/GHSA-vg6h-g5mr-9hgv
Type: github-advisory

## Affected
- Maven: `com.liferay.workspace:com.liferay.ticket.workspace` — affected >=0 <20240122.0632

## Details
Stored cross-site scripting (XSS) vulnerability in a custom object’s /o/c/<object-name> API endpoint in Liferay Portal 7.4.3.51 through 7.4.3.109, and Liferay DXP 2023.Q3.1 through 2023.Q3.4, 7.4 update 51 through update 92, and 7.3 update 33 through update 35 allows remote attackers to inject arbitrary web script or HTML via the externalReferenceCode parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43802
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43802
