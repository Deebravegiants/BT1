# [M] xwiki contains Exposed Dangerous Method or Function

## Summary
Severity: Medium
Advisory: GHSA-8692-g6g9-gm5p
CVE: CVE-2023-26478
CWE: CWE-749
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-8692-g6g9-gm5p
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-store-filesystem-oldcore` — affected >=14.3-rc-1 <14.4.6
- Maven: `org.xwiki.platform:xwiki-platform-store-filesystem-oldcore` — affected >=14.5 <14.9-rc-1

## Details
### Impact
`org.xwiki.store.script.TemporaryAttachmentsScriptService#uploadTemporaryAttachment` is returning an instance of `com.xpn.xwiki.doc.XWikiAttachment`. This class is not supported to be exposed to users without the `programing` right.
`com.xpn.xwiki.api.Attachment` should be used instead and takes case of checking the user's rights before performing dangerous operations.

### Patches
This has been patched in the version 14.9-rc-1 and 14.4.6.

### Workarounds
There's no workaround for this issue.

### References
https://jira.xwiki.org/browse/XWIKI-20180

### For more information
If you have any questions or comments about this advisory:

* Open an issue in [JIRA](https://jira.xwiki.org/)
* Email us at [security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-8692-g6g9-gm5p
- https://nvd.nist.gov/vuln/detail/CVE-2023-26478
- https://github.com/xwiki/xwiki-platform/commit/3c73c59e39b6436b1074d8834cf276916010014d
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20180
