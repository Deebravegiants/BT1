# [M] Nextcloud Server admin_audit does not log all actions on files in groupfolders

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2025-66552
Aliases: CVE-2025-66552, GHSA-ww9m-f8j4-jj9x
Ecosystem: Bitnami
Published: 2026-07-13
Source: https://osv.dev/vulnerability/BIT-nextcloud-2025-66552
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=32.0.0 <32.0.1

## Details
Nextcloud Server is a self hosted personal cloud system. In Nextcloud Server and Enterprise Server prior to 30.0.9 and 31.0.1, incorrect path handling with groupfolders caused the admin_audit app to not properly log all actions on files and folders inside groupfolders. This vulnerability is fixed in Nextcloud Server and Enterprise Server prior to 30.0.9 and 31.0.1.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-ww9m-f8j4-jj9x
- https://github.com/nextcloud/server/commit/7cc005c43c72bc384848cf8cb851895827c412f6
- https://github.com/nextcloud/server/pull/50992
- https://hackerone.com/reports/2890071
- https://nvd.nist.gov/vuln/detail/CVE-2025-66552
