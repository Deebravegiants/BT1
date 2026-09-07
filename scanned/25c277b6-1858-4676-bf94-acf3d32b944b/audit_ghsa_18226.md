# [M] Liferay Portal is vulnerable to Reflected XSS attack through get_editor path

## Summary
Severity: Medium
Advisory: GHSA-jhgr-j9cj-8j62
CVE: CVE-2025-43783
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-10
Source: https://github.com/advisories/GHSA-jhgr-j9cj-8j62
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.frontend.editor.ckeditor.web` — affected >=5.0.76 <5.0.102

## Details
A reflected cross-site scripting (XSS) vulnerability in Liferay Portal 7.4.3.73 through 7.4.3.128, and Liferay DXP 2024.Q3.0 through 2024.Q3.1, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.12, 7.4 update 73 through update 92 allows remote attackers to inject arbitrary web script or HTML via the /c/portal/comment/discussion/get_editor path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43783
- https://github.com/liferay/liferay-portal/commit/d7f9e94e0ebb63b04ac77d6253fe16dbd914bdf1
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18085
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43783
