# [C] XWiki Platform vulnerable to remote code execution via the edit action because it lacks CSRF token

## Summary
Severity: Critical
Advisory: GHSA-hgpw-6p4h-j6h5
CVE: CVE-2023-46242
CWE: CWE-352, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-07
Source: https://github.com/advisories/GHSA-hgpw-6p4h-j6h5
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=1.0 <14.10.7
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=15.0 <15.2-rc-1

## Details
### Impact

In XWiki Platform, it's possible to execute content with the right of any user if you can make this user follow a crafted URL. This is possible because edit action sets and thereby executes the page content without checking for a cross-site request forgert (CSRF) token.

To reproduce:
Get a user with programming rights to visit the URL `<xwiki-host>/xwiki/bin/edit/Main/?content=%7B%7Bgroovy%7D%7Dprintln%28%22Hello+from+Groovy%21%22%29%7B%7B%2Fgroovy%7D%7D&xpage=view`, where `<xwiki-host>` is the URL of your XWiki installation. This can be done by embedding an image with this URL.

The text "Hello from Groovy!" is displayed in the page content, showing that the Groovy macro has been executed. 

### Patches

This has been patched in XWiki 14.10.7 and 15.2-RC-1.

### Workarounds
There are no known workarounds for it.

### References

* https://jira.xwiki.org/browse/XWIKI-20386
* https://github.com/xwiki/xwiki-platform/commit/cf8eb861998ea423c3645d2e5e974420b0e882be

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-hgpw-6p4h-j6h5
- https://nvd.nist.gov/vuln/detail/CVE-2023-46242
- https://github.com/xwiki/xwiki-platform/commit/cf8eb861998ea423c3645d2e5e974420b0e882be
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20386
