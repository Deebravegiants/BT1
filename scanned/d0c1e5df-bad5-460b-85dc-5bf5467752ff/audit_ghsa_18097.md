# [M] Liferay Portal users can upload an unlimited amount of files

## Summary
Severity: Medium
Advisory: GHSA-84pp-qr92-95c9
CVE: CVE-2025-43762
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:L/SC:N/SI:L/SA:L (CVSS_V4)
Published: 2025-08-22
Source: https://github.com/advisories/GHSA-84pp-qr92-95c9
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.dynamic.data.mapping.form.web` — affected >=0 <4.0.180
- Maven: `com.liferay:com.liferay.dynamic.data.mapping.form.field.type` — affected >=0 <6.0.187

## Details
Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q1.0 through 2025.Q1.1, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.14 and 7.4 GA through update 92 allow users to upload an unlimited amount of files through the forms, the files are stored in the document_library allowing an attacker to cause a potential DDoS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43762
- https://github.com/liferay/liferay-portal/commit/9d32b089f30a42c8fd2d30832b3c90eefb5afe84
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18177
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43762
