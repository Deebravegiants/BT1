# [H] Liferay Portal and DXP Instance Admin can execute code using Objects Actions and Validations

## Summary
Severity: High
Advisory: GHSA-m5gv-vj3f-6v2p
CVE: CVE-2025-3586
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-m5gv-vj3f-6v2p
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.object.service` — affected >=0 <1.0.96

## Details
In Liferay Portal 7.4.3.27 through 7.4.3.42, and Liferay DXP 2024.Q1.1 through 2024.Q1.20, 2023.Q4.0 through 2023.Q4.10, 2023.Q3.1 through 2023.Q3.10, 7.4 update 27 through update 42 (Liferay PaaS, and Liferay Self-Hosted), the Objects module does not restrict the use of Groovy scripts in Object actions for Admin Users. This allows remote authenticated admin users with the Instance Administrator role to execute arbitrary Groovy scripts (i.e., remote code execution) through Object actions. 

In contrast, in Liferay DXP (Liferay SaaS), the use of Groovy in Object actions is not allowed due to the high security risks it poses. 

Starting from Liferay DXP 2024.Q2 and later, a new feature has been introduced in Instance Settings that allows administrators to configure whether Groovy scripts are allowed in their instances.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3586
- https://github.com/liferay/liferay-portal/commit/3b9e3bb1462ccd33ede05f73f45b38b8262f018f
- https://github.com/liferay/liferay-portal/commit/79ddc243e60864c0c30cfccb1cc46e705e922cb0
- https://github.com/liferay/liferay-portal/commit/b2aa19be228fb308ebe8ae1f47d3224e1fd06225
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17586
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-3586
