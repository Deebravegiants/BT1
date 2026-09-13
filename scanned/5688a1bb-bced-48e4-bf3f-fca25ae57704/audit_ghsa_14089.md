# [C] XWiki Platform vulnerable to RXSS via editor parameter - importinline template

## Summary
Severity: Critical
Advisory: GHSA-j9h5-vcgv-2jfm
CVE: CVE-2023-32071
CWE: CWE-116, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-09
Source: https://github.com/advisories/GHSA-j9h5-vcgv-2jfm
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-distribution-war` — affected >=2.2-milestone-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-distribution-war` — affected >=14.5 <14.10.4

## Details
### Impact

It's possible to execute javascript with the right of any user by leading him to a special URL on the wiki targeting a page which contains an attachment.

To reproduce:
* add an attachment to a page (for example, your user profile)
* add `?xpage=importinline&editor=%22%3E%3Cimg%20src%20onerror=alert(document.domain)%3E` to the page view URL as in `https://myhost/xwiki/bin/view/XWiki/MyUser?xpage=importinline&editor=%22%3E%3Cimg%20src%20onerror=alert(document.domain)%3E`

### Patches

This has been patched in XWiki 15.0-rc-1, 14.10.4 and 14.4.8.

### Workarounds

The easiest is to edit file `<xwiki app>/templates/importinline.vm` and apply the modification described on https://github.com/xwiki/xwiki-platform/commit/28905f7f518cc6f21ea61fe37e9e1ed97ef36f01

### References

https://jira.xwiki.org/browse/XWIKI-20340
https://app.intigriti.com/company/submissions/e95a7ad5-7029-4627-abf0-3e3e3ea0b4ce/XWIKI-E93DFEYK

### Attribution

This vulnerability has been reported on Intigriti by René de Sain @renniepak.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-j9h5-vcgv-2jfm
- https://nvd.nist.gov/vuln/detail/CVE-2023-32071
- https://github.com/xwiki/xwiki-platform/commit/28905f7f518cc6f21ea61fe37e9e1ed97ef36f01
- https://app.intigriti.com/company/submissions/e95a7ad5-7029-4627-abf0-3e3e3ea0b4ce/XWIKI-E93DFEYK
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20340
