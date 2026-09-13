# [M] Liferay Profile Widget does not prevent vCard extension spoofing

## Summary
Severity: Medium
Advisory: GHSA-pfxj-gvqg-mj44
CVE: CVE-2025-43824
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-07
Source: https://github.com/advisories/GHSA-pfxj-gvqg-mj44
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1 <7.4.3.112-ga112

## Details
The Profile Widget in Liferay Portal 7.4.0 through 7.4.3.111, and older unsupported versions, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.8, 7.4 GA through update 92, and older unsupported versions uses a user’s name in the “Content-Disposition” header, which allows remote authenticated users to change the file extension when a vCard file is downloaded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43824
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43824
