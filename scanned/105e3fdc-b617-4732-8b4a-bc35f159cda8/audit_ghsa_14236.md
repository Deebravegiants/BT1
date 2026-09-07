# [M] xwiki-platform-web-templates allows users to be created even when registration is disabled without validation via template macro

## Summary
Severity: Medium
Advisory: GHSA-fp36-mjw5-fmgx
CVE: CVE-2023-29513
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-fp36-mjw5-fmgx
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=8.0-rc-1 <14.10.1

## Details
### Impact

If a guest has view rights on any document, it's possible to create a new user using the `distribution/firstadminuser.wiki` in the wrong context.

To reproduce:

* On a wiki with view rights for guests but user registration disabled, open as guest <server>/xwiki/bin/view/Main?sheet=CKEditor.HTMLConverter&language=en&sourceSyntax=xwiki%2F2.1&stripHTMLEnvelope=true&fromHTML=false&toHTML=true&text=%7B%7Btemplate+name%3D%22distribution%2Ffirstadminuser.wiki%22+%2F%7D%7D where <server> is the URL of your XWiki installation.
* Enter username and password of your choice.
* Click "Register and login"

### Patches

The vulnerability has been patched in XWiki 15.0-rc-1 and 14.10.1.

### Workarounds
There is no known workaround other than upgrading.

### References
https://jira.xwiki.org/browse/XWIKI-19852
https://jira.xwiki.org/browse/XWIKI-20400

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-fp36-mjw5-fmgx
- https://nvd.nist.gov/vuln/detail/CVE-2023-29513
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19852
- https://jira.xwiki.org/browse/XWIKI-20400
