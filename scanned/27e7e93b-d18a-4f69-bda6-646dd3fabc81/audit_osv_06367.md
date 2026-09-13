# [M] BIT-liferay-2022-42130

## Summary
Severity: Medium
Advisory: BIT-liferay-2022-42130
Aliases: CVE-2022-42130, GHSA-mxvq-cv4x-p3jw
Ecosystem: Bitnami
Published: 2024-01-31
Source: https://osv.dev/vulnerability/BIT-liferay-2022-42130
Type: osv

## Affected
- Bitnami: `liferay` — affected >=7.4.0, >=7.2-fix.0

## Details
The Dynamic Data Mapping module in Liferay Portal 7.1.0 through 7.4.3.4, and Liferay DXP 7.1 before fix pack 27, 7.2 before fix pack 19, 7.3 before update 4, and 7.4 GA does not properly check permission of form entries, which allows remote authenticated users to view and access all form entries.

## References
- http://liferay.com
- https://issues.liferay.com/browse/LPE-17447
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-42130
