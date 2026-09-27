# [H] org.xwiki.platform:xwiki-platform-notifications-ui is missing checks for notification filter preferences editions

## Summary
Severity: High
Advisory: GHSA-r95w-889q-x2gx
CVE: CVE-2024-46978
CWE: CWE-648
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-r95w-889q-x2gx
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-notifications-ui` — affected >=13.2-rc-1 <14.10.21
- Maven: `org.xwiki.platform:xwiki-platform-notifications-ui` — affected >=15.0-rc-1 <15.5.5
- Maven: `org.xwiki.platform:xwiki-platform-notifications-ui` — affected >=15.6-rc-1 <15.10.1

## Details
### Impact

It's possible for any user knowing the ID of a notification filter preference of another user, to enable/disable it or even delete it. The impact is that the target user might start loosing notifications on some pages because of this.
This vulnerability is present in XWiki since 13.2-rc-1. 

### Patches

The vulnerability has been patched in XWiki 14.10.21, 15.5.5, 15.10.1, 16.0-rc-1. The patch consists in checking properly the rights of the user before performing any action on the filters. 

### Workarounds

It's possible to fix manually the vulnerability by editing the document `XWiki.Notifications.Code.NotificationPreferenceService` to apply the changes performed in this commit e8acc9d8e6af7dfbfe70716ded431642ae4a6dd4.

### References

  * JIRA ticket: https://jira.xwiki.org/browse/XWIKI-20337
  * Commit: e8acc9d8e6af7dfbfe70716ded431642ae4a6dd4

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

This vulnerability has been reported on Intigriti by @floerer

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-r95w-889q-x2gx
- https://nvd.nist.gov/vuln/detail/CVE-2024-46978
- https://github.com/xwiki/xwiki-platform/commit/4771573dac88e0cf04e30f1a8dfa183c048d503a
- https://github.com/xwiki/xwiki-platform/commit/99193a7e9a203b5bb8b2583ac96f5f4d56b9aa1a
- https://github.com/xwiki/xwiki-platform/commit/b9180b874a22e383ad5f2cd9e25bfed4594d4955
- https://github.com/xwiki/xwiki-platform/commit/e8acc9d8e6af7dfbfe70716ded431642ae4a6dd4
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20337
