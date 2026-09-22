# [M] org.xwiki.platform:xwiki-platform-oldcore may leak data through deleted and re-created documents

## Summary
Severity: Medium
Advisory: GHSA-gh64-qxh5-4m33
CVE: CVE-2023-37911
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-gh64-qxh5-4m33
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=9.4-rc-1 <14.10.8
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=15.0-rc-1 <15.3-rc-1

## Details
### Impact

When a document has been deleted and re-created, it is possible for users with view right on the re-created document but not on the deleted document to view the contents of the deleted document. Such a situation might arise when rights were added to the deleted document. This can be exploited through the diff feature and, partially, through the REST API by using versions such as `deleted:1` (where the number counts the deletions in the wiki and is thus guessable). Given sufficient rights, the attacker can also re-create the deleted document, thus extending the scope to any deleted document as long as the attacker has edit right in the location of the deleted document.

### Patches
This vulnerability has been patched in XWiki 14.10.8 and 15.3 RC1 by properly checking rights when deleted revisions of a document are accessed.

### Workarounds
The only workaround is to regularly [clean deleted documents](https://extensions.xwiki.org/xwiki/bin/view/Extension/Index%20Application#HPermanentlydeleteallpages) to minimize the potential exposure. Extra care should be taken when deleting sensitive documents that are protected individually (and not, e.g., by being placed in a protected space) or deleting a protected space as a whole.

### References
* https://jira.xwiki.org/browse/XWIKI-20685 (root cause)
* https://jira.xwiki.org/browse/XWIKI-20817 (exploitation via the diff feature)
* https://jira.xwiki.org/browse/XWIKI-20684 (exploitation via the REST API)
* https://github.com/xwiki/xwiki-platform/commit/f471f2a392aeeb9e51d59fdfe1d76fccf532523f

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-gh64-qxh5-4m33
- https://nvd.nist.gov/vuln/detail/CVE-2023-37911
- https://github.com/xwiki/xwiki-platform/commit/f471f2a392aeeb9e51d59fdfe1d76fccf532523f
- https://extensions.xwiki.org/xwiki/bin/view/Extension/Index%20Application#HPermanentlydeleteallpages
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20684
- https://jira.xwiki.org/browse/XWIKI-20685
- https://jira.xwiki.org/browse/XWIKI-20817
