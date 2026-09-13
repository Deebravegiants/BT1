# [M] Weblate: Team-enforced 2FA is bypassed for global permissions

## Summary
Severity: Medium
Advisory: CVE-2026-61790
Aliases: GHSA-x86c-ff69-cr2m
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-61790
Type: osv

## Details
Weblate is a web-based continuous localization platform used to manage software translations. In versions prior to 2026.7, a team can require its members to configure two-factor authentication before receiving the team's permissions, but this requirement is not enforced for site-wide global permissions. As a result, a user who belongs to a team that enforces 2FA and grants a global permission still receives that global permission even without 2FA configured, while the same requirement is correctly applied to project-, component-, and workspace-scoped permissions. Such a user can act on the granted global permission, including reaching the site management interface at /manage/. This issue is fixed in version 2026.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61790.json
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-x86c-ff69-cr2m
- https://nvd.nist.gov/vuln/detail/CVE-2026-61790
- https://github.com/WeblateOrg/weblate/commit/89042ab12268842655ddc10cb052bfc4dfa7a589
