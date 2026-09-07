# [M] Unprivileged XWiki Platform users can make arbitrary select queries using DatabaseListProperty and suggest.vm

## Summary
Severity: Medium
Advisory: GHSA-vpx4-7rfp-h545
CVE: CVE-2023-26473
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-vpx4-7rfp-h545
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=1.3-rc-1 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=14.0 <14.4.7
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=14.5 <14.10

## Details
### Impact

Any user with edit right can execute arbitrary database select and access data stored in the database.

To reproduce:
 * In admin, rights, remove scripting rights for {{XWikiAllGroup}}.
 * Create a new user without any special privileges.
 * Create a page "Private.WebHome" with {{TOKEN_42}} as content. Go to "page administration" and explicitly set all rights for "Admin" to remove them for all other users.
 * Logout and login as the unprivileged user. Ensure that the previously created page cannot be viewed.
 * Create a new page "ExploitClass.WebHome" and then open it in the class editor (first, make the user an advanced user).
 * Add a field named {{ContentList}} of type {{Database List}}
 * Enter in field "Hibernate Query" the following content: {noformat}select doc.content, doc.fullName from XWikiDocument as doc where doc.fullName = 'Private.WebHome'{noformat}
 * Save the class.
 * Open [http://localhost:8080/xwiki/bin/view/ExploitClass/?xpage=suggest&classname=ExploitClass.WebHome&fieldname=ContentList&firCol=doc.fullName&secCol=-]

### Patches

The problem has been patched on XWiki 13.10.11, 14.4.7, and 14.10.

### Workarounds

There is no workaround for this vulnerability other than upgrading.

### References

https://jira.xwiki.org/browse/XWIKI-19523

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-vpx4-7rfp-h545
- https://nvd.nist.gov/vuln/detail/CVE-2023-26473
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19523
