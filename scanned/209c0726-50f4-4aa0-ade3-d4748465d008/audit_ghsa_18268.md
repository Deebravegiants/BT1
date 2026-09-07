# [M] Liferay has a stored cross-site scripting (XSS) vulnerability via a a publication’s “Name” text field

## Summary
Severity: Medium
Advisory: GHSA-jh9h-8xf2-25wj
CVE: CVE-2025-43807
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-22
Source: https://github.com/advisories/GHSA-jh9h-8xf2-25wj
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.change.tracking.service` — affected >=0 <3.0.91

## Details
Stored cross-site scripting (XSS) vulnerability in the notifications widget in Liferay Portal 7.4.0 through 7.4.3.112, and Liferay DXP 2023.Q4.0 through 2023.Q4.8, 2023.Q3.1 through 2023.Q3.10, and 7.4 GA through update 92 allows remote attackers to inject arbitrary web scripts or HTML via a crafted payload injected into a publication’s “Name” text field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43807
- https://github.com/liferay/liferay-portal/commit/aaf32ff25affc0d63adc79abaedc9f565f033789
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17923
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43807
