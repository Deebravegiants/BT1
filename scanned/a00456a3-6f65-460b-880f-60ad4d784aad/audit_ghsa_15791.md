# [M] XWiki Platform vulnerable to document deletion and overwrite from edit

## Summary
Severity: Medium
Advisory: GHSA-33gp-gmg3-hfpq
CVE: CVE-2024-37898
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-33gp-gmg3-hfpq
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=13.10.4 <14.10.21
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=14.2 <14.10.21
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=15.0 <15.5.5
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=15.6-rc-1 <15.10.6

## Details
### Impact

When a user has edit but not view right on a page in XWiki, that user can delete the page and replace it by a page with new content without having delete right. The previous version of the page is moved into the recycle bin and can be restored from there by an admin. As the user is recorded as deleter, the user would in theory also be able to view the deleted content, but this is not directly possible as rights of the previous version are transferred to the new page and thus the user still doesn't have view right on the page. From all we examined, it therefore doesn't seem to be possible to exploit this to gain any rights.

To reproduce, just replace `view` by `edit` in the URL of a page that you cannot view but edit and save. This should send the page to the recycle bin and replace it by an empty one if the XWiki installation is vulnerable. After the fix, an error is displayed when saving.

### Patches
This has been patched in XWiki 14.10.21, 15.5.5 and 15.10.6 by cancelling save operations by users when a new document shall be saved despite the document's existing already.

### Workarounds
We're not aware of any workarounds.

### References
* https://jira.xwiki.org/browse/XWIKI-21553
* https://github.com/xwiki/xwiki-platform/commit/c5efc1e519e710afdf3c5f40c0fcc300ad77149f

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-33gp-gmg3-hfpq
- https://nvd.nist.gov/vuln/detail/CVE-2024-37898
- https://github.com/xwiki/xwiki-platform/commit/0bc27d6ec63c8a505ff950e2d1792cb4f773c22e
- https://github.com/xwiki/xwiki-platform/commit/56f5d8aab7371d5ba891168f73890806551322c5
- https://github.com/xwiki/xwiki-platform/commit/c5efc1e519e710afdf3c5f40c0fcc300ad77149f
- https://github.com/xwiki/xwiki-platform/commit/e4968fe268e5644ffd9bfa4ef6257d2796446009
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21553
