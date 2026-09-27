# [M] FroshAdminer Adminer UI is accessible without admin session

## Summary
Severity: Medium
Advisory: GHSA-f339-246p-wwjp
CVE: CVE-2026-25878
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-f339-246p-wwjp
Type: github-advisory

## Affected
- Packagist: `frosh/adminer-platform` — affected >=0 <2.2.1

## Details
### Summary
Unauthenticated access to Adminer UI

### Details
The Adminer route (/admin/adminer) was accessible without Shopware admin authentication. The route was configured with auth_required=false and performed no session validation, exposing the Adminer UI to unauthenticated users.

Note: Database access itself requires credentials that are only set through the ACL-protected API endpoint. Direct database access without prior admin login is not possible through this vulnerability alone.

### Impact
An unauthenticated user could access the Adminer interface, potentially disclosing version information or exploiting Adminer-specific vulnerabilities.

### Patches
Version 2.2.1 adds session validation. The Adminer route now verifies an authenticated session flag before rendering — returning HTTP 403 otherwise.

### Workarounds
Deactivate or uninstall the plugin.

## References
- https://github.com/FriendsOfShopware/FroshPlatformAdminer/security/advisories/GHSA-f339-246p-wwjp
- https://nvd.nist.gov/vuln/detail/CVE-2026-25878
- https://github.com/FriendsOfShopware/FroshPlatformAdminer/commit/c4dd6c3462af178b3a7d146d3c651c2c253e902b
- https://github.com/FriendsOfShopware/FroshPlatformAdminer
- https://github.com/FriendsOfShopware/FroshPlatformAdminer/releases/tag/2.2.1
