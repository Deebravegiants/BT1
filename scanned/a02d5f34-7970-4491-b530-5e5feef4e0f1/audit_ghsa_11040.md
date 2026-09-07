# [H] XWiki Blog Application home page vulnerable to Stored XSS via Post Title

## Summary
Severity: High
Advisory: GHSA-h2xq-h7f9-vh6c
CVE: CVE-2025-66024
CWE: CWE-116, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-h2xq-h7f9-vh6c
Type: github-advisory

## Affected
- Maven: `org.xwiki.contrib.blog:application-blog-ui` — affected >=9.15 <9.15.7

## Details
### Impact

The Blog Application is vulnerable to Stored Cross-Site Scripting (XSS) via the Blog Post Title. The vulnerability arises because the post title is injected directly into the HTML `<title>` tag without proper escaping.

An attacker with permissions to create or edit blog posts can inject malicious JavaScript into the title field. This script will execute in the browser of any user (including administrators) who views the blog post. This leads to potential session hijacking or privilege escalation.

To reproduce:

* Log in as a user with rights to create blog posts.
* Create a new blog post.
* In the Title field, insert the following payload designed to break out of the title tag: ```</title><script>alert('XSS in title blog')</script>```
* Save (Publish) the post.
* View the post in the blog home page

### Patches
The vulnerability has been patched in the blog application version 9.15.7 by adding missing escaping.

### Workarounds
We're not aware of any workarounds.

### References
* https://jira.xwiki.org/browse/BLOG-245
* https://github.com/xwiki-contrib/application-blog/commit/cca87f0a0edc2e7e049d46d51f4a4d8f78b714ba

### Attribution

Łukasz Rybak reported this vulnerability.

## References
- https://github.com/xwiki-contrib/application-blog/security/advisories/GHSA-h2xq-h7f9-vh6c
- https://nvd.nist.gov/vuln/detail/CVE-2025-66024
- https://github.com/xwiki-contrib/application-blog/commit/cca87f0a0edc2e7e049d46d51f4a4d8f78b714ba
- https://github.com/xwiki-contrib/application-blog/commit/cdcbf2816e9b329e8f006be4391a7ffe80d4bb3f
- https://github.com/xwiki-contrib/application-blog
- https://jira.xwiki.org/browse/BLOG-245
