# [H] BIT-liferay-2022-42125

## Summary
Severity: High
Advisory: BIT-liferay-2022-42125
Aliases: CVE-2022-42125, GHSA-g8hp-rc67-jf96
Ecosystem: Bitnami
Published: 2024-01-31
Source: https://osv.dev/vulnerability/BIT-liferay-2022-42125
Type: osv

## Affected
- Bitnami: `liferay` — affected >=7.4-update34.0

## Details
Zip slip vulnerability in FileUtil.unzip in Liferay Portal 7.4.3.5 through 7.4.3.35 and Liferay DXP 7.4 update 1 through update 34 allows attackers to create or overwrite existing files on the filesystem via the deployment of a malicious plugin/module.

## References
- http://liferay.com
- https://issues.liferay.com/browse/LPE-17517
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-42125
