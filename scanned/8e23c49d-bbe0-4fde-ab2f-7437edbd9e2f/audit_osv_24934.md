# [M] Unauthorized user can register an account in specific configurations in Zulip

## Summary
Severity: Medium
Advisory: CVE-2023-28623
Aliases: GHSA-7p62-pjwg-56rv
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2023-05-19
Source: https://osv.dev/vulnerability/CVE-2023-28623
Type: osv

## Details
Zulip is an open-source team collaboration tool with unique topic-based threading. In the event that 1: `ZulipLDAPAuthBackend` and an external authentication backend (any aside of `ZulipLDAPAuthBackend` and `EmailAuthBackend`) are the only ones enabled in `AUTHENTICATION_BACKENDS` in `/etc/zulip/settings.py` and 2: The organization permissions don't require invitations to join. An attacker can create a new account in the organization with an arbitrary email address in their control that's not in the organization's LDAP directory. The impact is limited to installations which have this specific combination of authentication backends as described above in addition to having `Invitations are required for joining this organization` organization permission disabled. This issue has been addressed in version 6.2. Users are advised to upgrade. Users unable to upgrade may enable the `Invitations are required for joining this organization` organization permission to prevent this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28623.json
- https://github.com/zulip/zulip/security/advisories/GHSA-7p62-pjwg-56rv
- https://nvd.nist.gov/vuln/detail/CVE-2023-28623
- https://github.com/zulip/zulip/commit/3df1b4dd7c210c21deb6f829df19412b74573f8d
