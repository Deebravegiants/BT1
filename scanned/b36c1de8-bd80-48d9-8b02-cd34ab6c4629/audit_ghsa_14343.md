# [C] XWiki Platform vulnerable to code injection from account through AWM view sheet

## Summary
Severity: Critical
Advisory: GHSA-jgrg-qvpp-9vwr
CVE: CVE-2023-29527
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-jgrg-qvpp-9vwr
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-appwithinminutes-ui` — affected >=7.4.4 <14.10.3

## Details
### Impact
Steps to reproduce:

1. As a user without script or programming right, edit your user profile (or any other document) with the wiki editor and add the content `{{groovy}}println("Hello " + "from Groovy!"){{/groovy}}`
1. Edit the document with the object editor and add an object of type AppWithinMinutes.LiveTableClass (no values need to be set, just save)
1. View the document

### Patches

The vulnerability has been patched in XWiki 15.0-rc-1 and 14.10.3.

### Workarounds

There is no known workaround.

### References

https://jira.xwiki.org/browse/XWIKI-20423

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-jgrg-qvpp-9vwr
- https://nvd.nist.gov/vuln/detail/CVE-2023-29527
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20423
