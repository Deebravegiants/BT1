# [M] org.xwiki.platform:xwiki-platform-notifications-ui leaks data of notification filters of users

## Summary
Severity: Medium
Advisory: GHSA-pg4m-3gp6-hw4w
CVE: CVE-2024-46979
CWE: CWE-200, CWE-359
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-pg4m-3gp6-hw4w
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-notifications-ui` — affected >=13.2-rc-1 <14.10.21
- Maven: `org.xwiki.platform:xwiki-platform-notifications-ui` — affected >=15.0-rc-1 <15.5.5
- Maven: `org.xwiki.platform:xwiki-platform-notifications-ui` — affected >=15.6-rc-1 <15.10.1

## Details
### Impact

It's possible to get access to notification filters of any user by using a URL such as `<hostname>xwiki/bin/get/XWiki/Notifications/Code/NotificationFilterPreferenceLivetableResults?outputSyntax=plain&type=custom&user=<username>`. This vulnerability impacts all versions of XWiki since 13.2-rc-1.
The filters do not provide much information (they mainly contain references which are public data in XWiki), though some info could be used in combination with other vulnerabilities.

### Patches

The vulnerability has been patched in XWiki 14.10.21, 15.5.5, 15.10.1, 16.0RC1. 
The patch consists in checking the rights of the user when sending the data.

### Workarounds

It's possible to workaround the vulnerability by applying manually the patch: it's possible for an administrator to edit directly the document `XWiki.Notifications.Code.NotificationFilterPreferenceLivetableResults` to apply the same changes as in the patch. See c8c6545f9bde6f5aade994aa5b5903a67b5c2582.

### References

  * Jira ticket: https://jira.xwiki.org/browse/XWIKI-20336
  * Commit: c8c6545f9bde6f5aade994aa5b5903a67b5c2582

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

This vulnerability has been reported on Intigriti by [Mete](https://www.linkedin.com/in/metehan-kalkan-5a3201199).

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-pg4m-3gp6-hw4w
- https://nvd.nist.gov/vuln/detail/CVE-2024-46979
- https://github.com/xwiki/xwiki-platform/commit/29e5edbb2b7068ada17290cea41e0aa8144e1294
- https://github.com/xwiki/xwiki-platform/commit/a0352922a1a61e0e858a9be89d73f0665630a63a
- https://github.com/xwiki/xwiki-platform/commit/c8c6545f9bde6f5aade994aa5b5903a67b5c2582
- https://github.com/xwiki/xwiki-platform/commit/ed090d1aa228848d3860968c437b72db3b09119f
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20336
