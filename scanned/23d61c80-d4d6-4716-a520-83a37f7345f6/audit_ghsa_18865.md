# [M] Liferay Portal reflected cross-site scripting (XSS) vulnerability in the google_gaget

## Summary
Severity: Medium
Advisory: GHSA-rx48-gqc2-4w47
CVE: CVE-2025-62249
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-10-21
Source: https://github.com/advisories/GHSA-rx48-gqc2-4w47
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0

## Details
A reflected cross-site scripting (XSS) vulnerability in the Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q3.0 through 2025.Q3.2, 2025.Q2.0 through 2025.Q2.12, 2025.Q1.0 through 2025.Q1.17, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.20, and 2023.Q4.0 through 2023.Q4.10 allows an remote non-authenticated attacker to inject JavaScript into the google_gadget.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62249
- https://github.com/liferay/liferay-portal/commit/66c51e026f7c9eee8f82137a586ceea5bdc081a5
- https://github.com/liferay/liferay-portal/commit/8309d01f151124e1af392b67baf9711e46488791
- https://github.com/liferay/liferay-portal/commit/f041e7058929618bb101b8e4bae5a8a226e6f8b8
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62249
