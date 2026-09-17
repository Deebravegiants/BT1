# [M] Liferay Portal User Enumeration Vulnerability via the Create Account Page

## Summary
Severity: Medium
Advisory: GHSA-xwc5-q44v-p6gg
CVE: CVE-2025-43751
CWE: CWE-203
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-08-22
Source: https://github.com/advisories/GHSA-xwc5-q44v-p6gg
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.login.web` — affected >=0 <6.0.66

## Details
User enumeration vulnerability in Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2024.Q4.0 through 2024.Q4.7, 2024.Q3.0 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.14, 2023.Q4.0 through 2023.Q4.10, 2023.Q3.1 through 2023.Q3.10 and 7.4 GA through update 92 allows remote attackers to determine if an account exist in the application via the create account page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43751
- https://github.com/liferay/liferay-portal/commit/097597e31b596295cb993bac596a42f06ac1e6d8
- https://github.com/liferay/liferay-portal/commit/1205e7bbcc31c40180935044d39ebf158b5256e1
- https://github.com/liferay/liferay-portal/commit/4843e000995ef5fbe4e4f14dce23c2f3116940de
- https://github.com/liferay/liferay-portal/commit/4987ff8641b970db3dca14d75bb9687120107c3b
- https://github.com/liferay/liferay-portal/commit/4f3b52bc92875cd0a0958ea33dece09b8224e6dc
- https://github.com/liferay/liferay-portal/commit/609104647a5a0bb79627ef689a2f8dc9fe9fbb05
- https://github.com/liferay/liferay-portal/commit/7b8376791cfe22bfce14e5f241af1d158d535fd8
- https://github.com/liferay/liferay-portal/commit/7e9e29a9dac8e5b6db6f2a480c98b483584b2f87
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18203
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43751
