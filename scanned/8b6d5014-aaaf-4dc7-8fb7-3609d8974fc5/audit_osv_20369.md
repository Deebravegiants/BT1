# [M] CVE-2021-33327

## Summary
Severity: Medium
Advisory: CVE-2021-33327
Aliases: GHSA-22wc-7wmm-v4cc
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-08-03
Source: https://osv.dev/vulnerability/CVE-2021-33327
Type: osv

## Details
The Portlet Configuration module in Liferay Portal 7.2.0 through 7.3.3, and Liferay DXP 7.0 fix pack pack 93 and 94, 7.1 fix pack 18, and 7.2 before fix pack 8, does not properly check user permission, which allows remote authenticated users to view the Guest and User role even if "Role Visibility" is enabled.

## References
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120747840
- https://issues.liferay.com/browse/LPE-17075
