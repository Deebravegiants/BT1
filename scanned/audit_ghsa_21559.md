# [C] Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection') in xwiki-platform-icon-ui

## Summary
Severity: Critical
Advisory: GHSA-5j7g-cf6r-g2h7
CVE: CVE-2022-41931
CWE: CWE-95
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-5j7g-cf6r-g2h7
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-icon-ui` — affected >=6.4-milestone-2 <13.10.7
- Maven: `org.xwiki.platform:xwiki-platform-icon-ui` — affected >=14.0.0 <14.4.2

## Details
### Impact
Any user with view rights on commonly accessible documents including the icon picker macro can execute arbitrary Groovy, Python or Velocity code in XWiki due to improper neutralization of the macro parameters of the icon picker macro.

The URL `<server>/xwiki/bin/view/Main?sheet=CKEditor.HTMLConverter&language=en&sourceSyntax=xwiki%252F2.1&stripHTMLEnvelope=true&fromHTML=false&toHTML=true&text=%7B%7BiconPicker%20id%3D%22'%3C%2Fscript%3E%7B%7B%2Fhtml%7D%7D%7B%7Bcache%7D%7D%7B%7Bgroovy%7D%7Dprintln(%2FHellofromIconPickerId%2F)%7B%7B%2Fgroovy%7D%7D%7B%7B%2Fcache%7D%7D%22%20class%3D%22'%3C%2Fscript%3E%7B%7B%2Fhtml%7D%7D%7B%7Bcache%7D%7D%7B%7Bgroovy%7D%7Dprintln(%2FHellofromIconPickerClass%2F)%7B%7B%2Fgroovy%7D%7D%7B%7B%2Fcache%7D%7D%22%2F%7D%7D` demonstrates the issue (replace `<server>` by the URL to your XWiki installation). If the output `HellofromIconPickerId` or `HellofromIconPickerClass` is visible, the XWiki installation is vulnerable (normally, all output should be contained in a script-tag and thus invisible).

### Patches

The problem has been patched in XWiki 13.10.7, 14.5 and 14.4.2.

### Workarounds

The [patch](https://github.com/xwiki/xwiki-platform/commit/47eb8a5fba550f477944eb6da8ca91b87eaf1d01) can be manually applied by editing `IconThemesCode.IconPickerMacro` in the object editor. The whole document can also be replaced by the current version by importing the document from the XAR archive of a fixed version as the only changes to the document have been security fixes and small formatting changes.

### References
* https://github.com/xwiki/xwiki-platform/commit/47eb8a5fba550f477944eb6da8ca91b87eaf1d01
* https://jira.xwiki.org/browse/XWIKI-19805

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-5j7g-cf6r-g2h7
- https://nvd.nist.gov/vuln/detail/CVE-2022-41931
- https://github.com/xwiki/xwiki-platform/commit/47eb8a5fba550f477944eb6da8ca91b87eaf1d01
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19805
