# [C] XWiki vulnerable to stored cross-site scripting via any wiki document and the displaycontent/rendercontent template

## Summary
Severity: Critical
Advisory: GHSA-fp7h-f9f5-x4q7
CVE: CVE-2023-34464
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-20
Source: https://github.com/advisories/GHSA-fp7h-f9f5-x4q7
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=2.2.1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=0 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=14.5 <14.10.5
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=15.0-rc-1 <15.1-rc-1

## Details
### Impact

Any user who can edit a document in a wiki like the user profile can create a stored XSS attack by putting plain HTML code into that document and then tricking another user to visit that document with the `displaycontent` or `rendercontent` template and plain output syntax. For example, edit any document with the wiki editor and set the content to `<script>alert(1)</script>` , save and then append the parameters `?viewer=displaycontent&sheet=&outputSyntax=plain`. If this displays an alert, the installation is vulnerable. If a user with programming rights is tricked into visiting such a URL, arbitrary actions be performed with this user's rights, impacting the confidentiality, integrity, and availability of the whole XWiki installation.

### Patches
This has been patched in XWiki 14.4.8, 14.10.5 and 15.1RC1 by setting the content type of the response to plain text when the output syntax is not an HTML syntax.

### Workarounds
The [patch](https://github.com/xwiki/xwiki-platform/commit/53e8292a31ec70fba5e1d705a4ac443658b9e6df#diff-e332fba67335bd2202bdac144be7cd244a16cef0ccee741f9c20025a981027d5) can be manually applied to the `rendercontent.vm` template in an existing installation to patch this vulnerability without upgrading.

### References
* https://jira.xwiki.org/browse/XWIKI-20290
* https://github.com/xwiki/xwiki-platform/commit/53e8292a31ec70fba5e1d705a4ac443658b9e6df

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-fp7h-f9f5-x4q7
- https://nvd.nist.gov/vuln/detail/CVE-2023-34464
- https://github.com/xwiki/xwiki-platform/commit/53e8292a31ec70fba5e1d705a4ac443658b9e6df
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20290
