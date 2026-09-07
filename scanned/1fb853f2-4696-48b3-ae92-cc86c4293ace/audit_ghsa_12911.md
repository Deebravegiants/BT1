# [C] XWiki CKEditor.HTMLConverter vulnerable to Remote Code Execution via Cross-Site Request Forgery

## Summary
Severity: Critical
Advisory: GHSA-6mjp-2rm6-9g85
CVE: CVE-2023-22457
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-06
Source: https://github.com/advisories/GHSA-6mjp-2rm6-9g85
Type: github-advisory

## Affected
- Maven: `org.xwiki.contrib:application-ckeditor-ui` — affected >=0 <1.64.3

## Details
### Impact
The `CKEditor.HTMLConverter` document lacked a protection against Cross-Site Request Forgery (CSRF), allowing to execute macros with the rights of the current user. If a privileged user with programming rights was tricked into executing a GET request to this document with certain parameters (e.g., via an image with a corresponding URL embedded in a comment or via a redirect), this would allow arbitrary remote code execution and the attacker could gain rights, access private information or impact the availability of the wiki.

The attack can be demonstrated by accessing the URL `<server>/xwiki/bin/view/Main?sheet=CKEditor.HTMLConverter&language=en&sourceSyntax=xwiki%2F2.1&stripHTMLEnvelope=true&fromHTML=false&toHTML=true&text=%7B%7Bgroovy%7D%7Dprintln%28%22Hello+from+Groovy%21%22%29%7B%7B%2Fgroovy%7D%7D` where `<server>` is the URL of the XWiki installation as a user with programming rights. If this displays the text "Hello from Groovy!", the installation is vulnerable.

### Patches
The issue has been patched in the CKEditor Integration version 1.64.3. This has also been patched in the version of the CKEditor integration that is bundled starting with XWiki 14.6 RC1.

### Workarounds
There are no known workarounds for this other than upgrading the CKEditor integration to a fixed version.

### References
* https://github.com/xwiki-contrib/application-ckeditor/commit/6b1053164386aefc526df7512bc664918aa6849b
* https://jira.xwiki.org/browse/CKEDITOR-475

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki-contrib/application-ckeditor/security/advisories/GHSA-6mjp-2rm6-9g85
- https://nvd.nist.gov/vuln/detail/CVE-2023-22457
- https://github.com/xwiki-contrib/application-ckeditor/commit/6b1053164386aefc526df7512bc664918aa6849b
- https://github.com/xwiki-contrib/application-ckeditor
- https://jira.xwiki.org/browse/CKEDITOR-475
