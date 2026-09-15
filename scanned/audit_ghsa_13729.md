# [H] XWiki Platform vulnerable to privilege escalation and remote code execution via the edit action

## Summary
Severity: High
Advisory: GHSA-g2qq-c5j9-5w5w
CVE: CVE-2023-46243
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-07
Source: https://github.com/advisories/GHSA-g2qq-c5j9-5w5w
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=15.0 <15.2-rc-1
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=1.0 <14.10.6

## Details
### Impact

In XWiki Platform, it's possible for a user to execute any content with the right of an existing document's content author, provided the user have edit right on it. The reason for this is that the edit action sets the content without modifying the content author.

To reproduce:
* Log in as a user without programming or script right.
* Open the URL `<xwiki-host>/xwiki/bin/edit/<document>/?content=%7B%7Bgroovy%7D%7Dprintln%28%22Hello+from+Groovy%21%22%29%7B%7B%2Fgroovy%7D%7D&xpage=view`, where `<xwiki-host>` is the URL of your XWiki installation and `<document>` is the path to a document whose content author has programming right (or script right) and on which the current user has edit right.

The text "Hello from Groovy!" is displayed in the page content, showing that the Groovy macro has been executed, which should not be the case for a user without programming right.

### Patches

This has been patched in XWiki 14.10.6 and 15.2RC1.

### Workarounds

There are no known workarounds for it.

### References

* https://jira.xwiki.org/browse/XWIKI-20385
* https://github.com/xwiki/xwiki-platform/commit/a0e6ca083b36be6f183b9af33ae735c1e02010f4

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-g2qq-c5j9-5w5w
- https://nvd.nist.gov/vuln/detail/CVE-2023-46243
- https://github.com/xwiki/xwiki-platform/commit/a0e6ca083b36be6f183b9af33ae735c1e02010f4
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20385
