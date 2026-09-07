# [C] XWiki Platform's Mail.MailConfig can be edited by any user with edit rights

## Summary
Severity: Critical
Advisory: GHSA-g75c-cjr6-39mc
CVE: CVE-2023-34465
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-20
Source: https://github.com/advisories/GHSA-g75c-cjr6-39mc
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-mail-send-default` — affected >=11.8-rc-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-mail-send-default` — affected >=14.5 <14.10.6
- Maven: `org.xwiki.platform:xwiki-platform-mail-send-default` — affected >=15.0-rc-1 <15.1

## Details
### Impact

`Mail.MailConfig` can be edited by any logged-in user by default. Consequently, they can:
- change the mail obfuscation configuration
- view and edit the mail sending configuration, including the smtp domain name and credentials.

### Patches
The problem has been patched on XWiki 14.4.8, 15.1, and 14.10.6.

### Workarounds
The rights of the `Mail.MailConfig` page can be manually updated so that only a set of trusted users can view, edit and delete it (e.g., the `XWiki.XWikiAdminGroup` group).
On 14.4.8+, 15.1-rc-1+, or 14.10.5+, if at startup `Mail.MailConfig` does not have any rights defined, `view`, `edit ` and `delete` rights are automatically granted to the `XWiki.XWikiAdminGroup` group.
See the corresponding [patch](https://github.com/xwiki/xwiki-platform/commit/d28d7739089e1ae8961257d9da7135d1a01cb7d4).

### References
- https://jira.xwiki.org/browse/XWIKI-20519 + https://jira.xwiki.org/browse/XWIKI-20671
- https://github.com/xwiki/xwiki-platform/commit/d28d7739089e1ae8961257d9da7135d1a01cb7d4
- https://github.com/xwiki/xwiki-platform/commit/8910b8857d3442d2e8142f655fdc0512930354d1


### For more information

If you have any questions or comments about this advisory:

*    Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
*    Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-g75c-cjr6-39mc
- https://nvd.nist.gov/vuln/detail/CVE-2023-34465
- https://github.com/xwiki/xwiki-platform/commit/8910b8857d3442d2e8142f655fdc0512930354d1
- https://github.com/xwiki/xwiki-platform/commit/d28d7739089e1ae8961257d9da7135d1a01cb7d4
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20519
- https://jira.xwiki.org/browse/XWIKI-20671
