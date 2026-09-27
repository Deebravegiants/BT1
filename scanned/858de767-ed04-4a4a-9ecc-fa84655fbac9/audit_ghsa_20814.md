# [H] XWiki Platform Web Templates vulnerable to Missing Authorization, Exposure of Private Personal Information to Unauthorized Actor

## Summary
Severity: High
Advisory: GHSA-599v-w48h-rjrm
CVE: CVE-2022-36091
CWE: CWE-359, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-599v-w48h-rjrm
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=1.3 <13.10.4
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=14.0 <14.2

## Details
### Impact
Through the suggestion feature, string and list properties of objects the user shouldn't have access to can be accessed. This includes private personal information like email addresses and salted password hashes of registered users but also other information stored in properties of objects. Sensitive configuration fields like passwords for LDAP or SMTP servers could be accessed. By exploiting an additional vulnerability, this issue can even be exploited on [private wikis](https://www.xwiki.org/xwiki/bin/view/Documentation/AdminGuide/Access%20Rights/#HPrivateWiki) at least for string properties.

### Patches
The issue is patched in version 13.10.4 and 14.2. Password properties are no longer displayed and rights are checked for other properties.

### Workarounds
The template file `suggest.vm` can be replaced by a patched version without upgrading or restarting XWiki unless it has been [overridden](https://extensions.xwiki.org/xwiki/bin/view/Extension/Skin%20Application#HHowtooverrideatemplate), in which case the overridden template should be patched, too. This might need adjustments for older versions, though.

### References
* https://jira.xwiki.org/browse/XWIKI-18849

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org)
* Email us at [security mailing-list](mailto:security@xwiki.com)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-599v-w48h-rjrm
- https://nvd.nist.gov/vuln/detail/CVE-2022-36091
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-18849
