# [M] Liferay Portal's Unlimited File Upload Could Result in DoS

## Summary
Severity: Medium
Advisory: GHSA-qpp6-f3qj-rggq
CVE: CVE-2025-43752
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:L/SC:N/SI:L/SA:L (CVSS_V4)
Published: 2025-08-22
Source: https://github.com/advisories/GHSA-qpp6-f3qj-rggq
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1

## Details
Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q1.0 through 2025.Q1.4, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.15 and 7.4 GA through update 92 allow users to upload an unlimited amount of files through the object entries attachment fields, the files are stored in the document_library allowing an attacker to cause a potential DDoS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43752
- https://github.com/liferay/liferay-portal/commit/45dda30252d83912307491d8ed8802577871fa25
- https://github.com/liferay/liferay-portal/commit/f3e4723acdf15d3f690d401d6eb6a5653e5be391
- https://github.com/liferay/liferay-portal/commit/fffed67b3fd1cc6071fd25a9b104b7691ffea2f8
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18188
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43752
