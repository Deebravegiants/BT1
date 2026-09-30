# [H] XWiki Blog Application: Privilege Escalation (PR) from account through blog content

## Summary
Severity: High
Advisory: GHSA-gwj6-xpfg-pxwr
CVE: CVE-2025-58365
CWE: CWE-250, CWE-94, CWE-95
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-08
Source: https://github.com/advisories/GHSA-gwj6-xpfg-pxwr
Type: github-advisory

## Affected
- Maven: `org.xwiki.contrib.blog:application-blog-ui` — affected >=0 <9.14

## Details
### Impact
The blog application in XWiki allowed remote code execution for any user who has edit right on any page. Normally, these are all logged-in users as they can edit their own user profile. To exploit, it is sufficient to add an object of type `Blog.BlogPostClass` to any page and to add some script macro with the exploit code to the "Content" field of that object.

### Patches
The vulnerability has been patched in the blog application version 9.14 by executing the content of blog posts with the rights of the appropriate author.

### Workarounds
We're not aware of any workarounds.

### Resources
* https://jira.xwiki.org/browse/BLOG-191
* https://github.com/xwiki-contrib/application-blog/commit/b98ab6f17da3029576f42d12b4442cd555c7e0b4

## References
- https://github.com/xwiki-contrib/application-blog/security/advisories/GHSA-gwj6-xpfg-pxwr
- https://nvd.nist.gov/vuln/detail/CVE-2025-58365
- https://github.com/xwiki-contrib/application-blog/commit/b98ab6f17da3029576f42d12b4442cd555c7e0b4
- https://github.com/xwiki-contrib/application-blog
- https://jira.xwiki.org/browse/BLOG-191
