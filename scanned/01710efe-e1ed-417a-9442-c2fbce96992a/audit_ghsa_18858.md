# [M] Liferay Account Admin Web vulnerable to Authorization Bypass Through User-Controlled Key 

## Summary
Severity: Medium
Advisory: GHSA-3cm9-jrf5-h2cx
CVE: CVE-2025-62242
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-10-13
Source: https://github.com/advisories/GHSA-3cm9-jrf5-h2cx
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.change.tracking.web` — affected >=0 <2.0.120

## Details
Insecure Direct Object Reference (IDOR) vulnerability with account addresses in Liferay Portal 7.4.3.4 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.8, and 7.4 GA through update 92 allows remote authenticated users to from one account to view addresses from a different account via the _com_liferay_account_admin_web_internal_portlet_AccountEntriesAdminPortlet_addressId parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62242
- https://github.com/liferay/liferay-portal/commit/dd89fff675f04d146fda38a1bec884cf40d0c756
- https://github.com/liferay/liferay-portal/commit/fa356d07ab239e790b7e460d33c25184aef58716
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17932
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62245
