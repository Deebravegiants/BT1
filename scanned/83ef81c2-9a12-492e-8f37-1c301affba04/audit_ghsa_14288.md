# [M] XWiki App Within Minutes app grants space admin rights that allows cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-44h9-xxvx-pg6x
CVE: CVE-2023-29515
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-44h9-xxvx-pg6x
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-appwithinminutes` — affected >=4.0-milestone-2 <4.2-milestone-1
- Maven: `org.xwiki.platform:xwiki-platform-appwithinminutes-ui` — affected >=4.2-milestone-1 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-appwithinminutes-ui` — affected >=14.0-rc-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-appwithinminutes-ui` — affected >=14.5 <14.10.1

## Details
### Impact
Any user who can create a space can become admin of that space through App Within Minutes. The admin right implies the script right and thus allows JavaScript injection. The vulnerability can be exploited by creating an app in App Within Minutes. If the button should be disabled because the user doesn't have global edit right, the app can also be created by directly opening `/xwiki/bin/view/AppWithinMinutes/CreateApplication?wizard=true` on the XWiki installation.

### Patches
This has been patched in XWiki 13.10.11, 14.4.8, 14.10.1 and 15.0 RC1 by not granting the space admin right if the user doesn't have script right on the space where the app is created. Error message are displayed to warn the user that the app will be broken in this case. Users who became space admin through this vulnerability won't loose the space admin right due to the fix, so it is advised to check if all users who created AWM apps should keep their space admin rights.

### Workarounds
The patch can be applied by patching the affected wiki documents, the most important one being `AppWithinMinutes.LiveTableEditSheet`. Further, the attack can be prevented by denying view access to `AppWithinMinutes.LiveTableEditSheet`. This only impacts creation and editing of App Within Minutes apps.

### References

* https://jira.xwiki.org/browse/XWIKI-20190
* https://github.com/xwiki/xwiki-platform/commit/e73b890623efa604adc484ad82f37e31596fe1a6

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-44h9-xxvx-pg6x
- https://nvd.nist.gov/vuln/detail/CVE-2023-29515
- https://github.com/xwiki/xwiki-platform/commit/e73b890623efa604adc484ad82f37e31596fe1a6
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20190
