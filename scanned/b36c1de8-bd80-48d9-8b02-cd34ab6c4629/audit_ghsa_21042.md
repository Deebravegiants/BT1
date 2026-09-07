# [H] XWiki Platform vulnerable to Cross-site Scripting in the deleted attachments list

## Summary
Severity: High
Advisory: GHSA-gjmq-x5x7-wc36
CVE: CVE-2022-36096
CWE: CWE-79, CWE-80
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-gjmq-x5x7-wc36
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-index-ui` — affected >=2.2-milestone-1 <13.10.6
- Maven: `org.xwiki.platform:xwiki-platform-index-ui` — affected >=14.0 <14.3

## Details
### Impact

It's possible to store a JavaScript which will be executed by anyone viewing the deleted attachments index with an attachment containing javascript in its name.

For example, attachment a file with name `><img src=1 onerror=alert(1)>.jpg` will execute the alert.

### Patches

This issue has been patched in XWiki 13.10.6 and 14.3.

### Workarounds

It is possible to modify fix the vulnerability by editing the wiki page `XWiki.DeletedAttachments` with the object editor, open the `JavaScriptExtension` object and apply on the content the changes that can be found on the commit https://github.com/xwiki/xwiki-platform/commit/6705b0cd0289d1c90ed354bd4ecc1508c4b25745.

### References

* https://jira.xwiki.org/browse/XWIKI-19613

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-gjmq-x5x7-wc36
- https://nvd.nist.gov/vuln/detail/CVE-2022-36096
- https://github.com/xwiki/xwiki-platform/commit/6705b0cd0289d1c90ed354bd4ecc1508c4b25745
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19613
