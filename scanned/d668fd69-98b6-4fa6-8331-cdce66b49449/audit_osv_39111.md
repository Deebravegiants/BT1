# [C] Suspended or inactive FOSSBilling accounts can retain or regain access through existing sessions, API tokens, and password reset flows

## Summary
Severity: Critical
Advisory: CVE-2026-43918
Aliases: GHSA-qv6c-v49w-8g2j
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-43918
Type: osv

## Details
FOSSBilling is a free, open-source billing and client management system. Prior to version 0.8.0, when a client or staff/admin account is suspended or marked inactive, existing authenticated sessions are not invalidated. The session identity loaders in src/di.php (loggedin_client and loggedin_admin) only reject sessions if the backing account record no longer exists in the database. They do not verify that the account's status is still active. This allows a suspended or deactivated user to retain full access until their session naturally expires. This issue has been fixed in version 0.8.0.

## References
- https://github.com/FOSSBilling/FOSSBilling/releases/tag/0.8.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43918.json
- https://github.com/FOSSBilling/FOSSBilling/security/advisories/GHSA-qv6c-v49w-8g2j
- https://nvd.nist.gov/vuln/detail/CVE-2026-43918
