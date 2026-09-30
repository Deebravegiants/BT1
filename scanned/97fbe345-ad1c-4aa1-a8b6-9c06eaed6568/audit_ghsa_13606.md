# [H] Privilege escalation (PR)/remote code execution from account through Menu.UIExtensionSheet

## Summary
Severity: High
Advisory: GHSA-v2rr-xw95-wcjx
CVE: CVE-2023-37909
CWE: CWE-94, CWE-95
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-v2rr-xw95-wcjx
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-menu` — affected >=5.1-rc-1 <14.10.8
- Maven: `org.xwiki.platform:xwiki-platform-menu-ui` — affected >=5.1-rc-1 <14.10.8
- Maven: `org.xwiki.platform:xwiki-platform-menu-ui` — affected >=15.0-rc-1 <15.3-rc-1

## Details
### Impact
Any user who can edit their own user profile can execute arbitrary script macros including Groovy and Python macros that allow remote code execution including unrestricted read and write access to all wiki contents. This can be reproduced with the following steps:

1. As an advanced user, use the object editor to add an object of type `UIExtensionClass` to your user profile. Set the value "Extension Point ID" to `{{/html}}{{async async=false cache=false}}{{groovy}}println("Hello from Groovy!"){{/groovy}}{{/async}}`
2. Open `<xwiki-host>/xwiki/bin/edit/XWiki/<username>?sheet=Menu.UIExtensionSheet` where `<xwiki-host>` is the URL of your XWiki installation and `<username>` is your user name.

If the text `Hello from Groovy!" selected="selected">` is displayed in the output, the attack succeeded.

### Patches

This has been patched in XWiki 14.10.8 and 15.3 RC1 by adding proper escaping.

### Workarounds
The [patch](https://github.com/xwiki/xwiki-platform/commit/9e8f080094333dec63a8583229a3799208d773be#diff-47a5652d0c8e4601dac12bd9ab34b8bd688cb22a1b758ce7b774043658834662) can be manually applied to the document `Menu.UIExtensionSheet`, only three lines need to be changed.

### References

* https://jira.xwiki.org/browse/XWIKI-20746
* https://github.com/xwiki/xwiki-platform/commit/9e8f080094333dec63a8583229a3799208d773be

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-v2rr-xw95-wcjx
- https://nvd.nist.gov/vuln/detail/CVE-2023-37909
- https://github.com/xwiki/xwiki-platform/commit/9e8f080094333dec63a8583229a3799208d773be
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20746
