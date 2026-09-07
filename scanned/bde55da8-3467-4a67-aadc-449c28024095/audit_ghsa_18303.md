# [M] Liferay Contacts Center widget has insecure direct object reference

## Summary
Severity: Medium
Advisory: GHSA-8c8v-r5jj-4425
CVE: CVE-2025-43803
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-19
Source: https://github.com/advisories/GHSA-8c8v-r5jj-4425
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.contacts.web` — affected >=0 <5.0.59

## Details
Insecure direct object reference (IDOR) vulnerability in the Contacts Center widget in Liferay Portal 7.4.0 through 7.4.3.119, and older unsupported versions, and Liferay DXP 2023.Q4.0 through 2023.Q4.6, 2023.Q3.1 through 2023.Q3.10, 7.4 GA through update 92, and older unsupported versions allows remote attackers to view contact information, including the contact’s name and email address, via the _com_liferay_contacts_web_portlet_ContactsCenterPortlet_entryId parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43803
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43803
