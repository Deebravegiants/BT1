# [M] Cross-site Scripting by SVG upload in xwiki-platform

## Summary
Severity: Medium
Advisory: GHSA-9jq9-c2cv-pcrj
CVE: CVE-2021-43841
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-9jq9-c2cv-pcrj
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=0 <12.10.6
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=13.0 <13.3RC1
- Maven: `org.xwiki.platform:xwiki-platform-tool-configuration-resources` — affected >=13.0 <13.3RC1
- Maven: `org.xwiki.platform:xwiki-platform-tool-configuration-resources` — affected >=0 <12.10.6

## Details
### Impact
When using default XWiki configuration, it's possible for an attacker to upload an SVG containing a script executed when executing the download action on the file. 

### Patches
This problem has been patched so that the default configuration doesn't allow to display the SVG files in the browser.

### Workarounds
This issue can be fixed without the patch by setting properly the configuration to download or display files, see: https://www.xwiki.org/xwiki/bin/view/Documentation/AdminGuide/Attachments#HAttachmentdisplayordownload

### References
https://jira.xwiki.org/browse/XWIKI-18368

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira](http://jira.xwiki.org)
* Email us at [security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-9jq9-c2cv-pcrj
- https://nvd.nist.gov/vuln/detail/CVE-2021-43841
- https://github.com/xwiki/xwiki-platform/commit/5853d492b3a274db0d94d560e2a5ea988a271c62
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-18368
- https://www.xwiki.org/xwiki/bin/view/Documentation/AdminGuide/Attachments#HAttachmentdisplayordownload
