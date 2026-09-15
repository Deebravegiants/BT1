# [C] XWiki Platform: Privilege escalation (PR) from user registration through PDFClass

## Summary
Severity: Critical
Advisory: GHSA-vxwr-wpjv-qjq7
CVE: CVE-2024-31981
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-vxwr-wpjv-qjq7
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=3.0.1 <14.10.20
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=15.0-rc-1 <15.5.4
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=15.6-rc-1 <15.10-rc-1

## Details
### Impact
Remote code execution is possible via PDF export templates.
To reproduce on an installation, register a new user account with username `PDFClass` if `XWiki.PDFClass` does not exist.
On `XWiki.PDFClass`, use the class editor to add a "style" property of type "TextArea" and content type "Plain Text".
Then, add an object of class `PDFClass` and set the "style" attribute to `$services.logging.getLogger('PDFClass').error("I got programming: $services.security.authorization.hasAccess('programming')")`.
Finally, go to `<host>/xwiki/bin/export/Main/WebHome?format=pdf&pdftemplate=XWiki.PDFClass`. If the logs contain "ERROR PDFClass - I got programming: true", the instance is vulnerable.

### Patches
This vulnerability has been patched in XWiki 14.10.20, 15.5.4 and 15.10-rc-1.

### Workarounds
If PDF templates are not typically used on the instance, an administrator can create the document `XWiki.PDFClass` and block its edition, after making sure that it does not contain a `style` attribute.
Otherwise, the instance needs to be updated.

### References
- https://jira.xwiki.org/browse/XWIKI-21337
- https://github.com/xwiki/xwiki-platform/commit/d28e21a670c69880b951e415dd2ddd69d273eae9

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-vxwr-wpjv-qjq7
- https://nvd.nist.gov/vuln/detail/CVE-2024-31981
- https://github.com/xwiki/xwiki-platform/commit/480186f9d2fca880513da8bc5a609674d106cbd3
- https://github.com/xwiki/xwiki-platform/commit/a4ad14d9c1605a5ab957237e505ebbb29f5b9d73
- https://github.com/xwiki/xwiki-platform/commit/d28e21a670c69880b951e415dd2ddd69d273eae9
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21337
