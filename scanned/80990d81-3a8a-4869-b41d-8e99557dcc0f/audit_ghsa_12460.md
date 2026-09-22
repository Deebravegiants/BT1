# [H] Velocity execution without script right through tree macro

## Summary
Severity: High
Advisory: GHSA-p5f8-qf24-24cj
CVE: CVE-2023-50732
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-12-19
Source: https://github.com/advisories/GHSA-p5f8-qf24-24cj
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-index-tree-macro` — affected >=8.3-rc-1 <14.10.7
- Maven: `org.xwiki.platform:xwiki-platform-index-tree-macro` — affected >=15.0-rc-1 <15.2-rc-1

## Details
### Impact

It's possible to execute a Velocity script without script right through the document tree.

To reproduce:

* As a user without script right, create a document, e.g., named Nasty Title
* Set the document's title to `$request.requestURI`
* Click "Save & View"
* Reload the page in the browser

The navigation panel displays a document named with the current URL, showing that the Velocity code has been executed even though the user doesn't have script right.

### Patches

This has been patched in XWiki 14.10.7 and 15.2RC1.

### Workarounds

A possible workaround is to:
* modify the page XWiki.DocumentTreeMacros
* search for the code `#set ($discard = $translatedDocument.setTitle($translatedDocument.title))`
* modify it into `#set ($discard = $translatedDocument.setcomment(''))`

### References

* https://jira.xwiki.org/browse/XWIKI-20625
* https://github.com/xwiki/xwiki-platform/commit/41d7dca2d30084966ca6a7ee537f39ee8354a7e3

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-p5f8-qf24-24cj
- https://nvd.nist.gov/vuln/detail/CVE-2023-50732
- https://github.com/xwiki/xwiki-platform/commit/41d7dca2d30084966ca6a7ee537f39ee8354a7e3
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20625
