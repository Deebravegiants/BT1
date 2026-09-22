# [M] BIT-liferay-2022-42127

## Summary
Severity: Medium
Advisory: BIT-liferay-2022-42127
Aliases: CVE-2022-42127, GHSA-5x9h-p2gx-35mg
Ecosystem: Bitnami
Published: 2024-01-31
Source: https://osv.dev/vulnerability/BIT-liferay-2022-42127
Type: osv

## Affected
- Bitnami: `liferay` — affected >=7.4-update36.0

## Details
The Friendly Url module in Liferay Portal 7.4.3.5 through 7.4.3.36, and Liferay DXP 7.4 update 1 though 36 does not properly check user permissions, which allows remote attackers to obtain the history of all friendly URLs that was assigned to a page.

## References
- http://liferay.com
- https://issues.liferay.com/browse/LPE-17607
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-42127
