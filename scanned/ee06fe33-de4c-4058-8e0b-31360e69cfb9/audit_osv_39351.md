# [M] Nextcloud: Wrong condition in the User OIDC app's LdapService allowed deleted LDAP users to authenticate

## Summary
Severity: Medium
Advisory: CVE-2026-45284
Aliases: GHSA-79xf-ffj8-96fm
CVSS: 4.6 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45284
Type: osv

## Details
Nextcloud is an open source content collaboration platform. From version 1.3.6 to before version 8.4.0, an improper check allowed users that where provided by LDAP to still authenticate towards user OIDC after they where deleted. This issue has been patched in version 8.4.0.

## References
- https://hackerone.com/reports/3554696
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45284.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-79xf-ffj8-96fm
- https://nvd.nist.gov/vuln/detail/CVE-2026-45284
- https://github.com/nextcloud/user_oidc/pull/1340
