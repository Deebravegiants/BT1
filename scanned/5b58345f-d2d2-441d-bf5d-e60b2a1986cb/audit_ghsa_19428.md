# [C] org.xwiki.contrib.markdown:syntax-markdown-commonmark12 vulnerable to XSS via Markdown content

## Summary
Severity: Critical
Advisory: GHSA-8g2j-rhfh-hq3r
CVE: CVE-2025-46558
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-30
Source: https://github.com/advisories/GHSA-8g2j-rhfh-hq3r
Type: github-advisory

## Affected
- Maven: `org.xwiki.contrib.markdown:syntax-markdown-commonmark12` — affected >=8.2 <8.9

## Details
### Impact
The Markdown syntax is vulnerable to XSS through HTML. In particular, using Markdown syntax, it's possible for any user to embed Javascript code that will then be executed on the browser of any other user visiting either the document or the comment that contains it. In the instance that this code is executed by a user with admins or programming rights, this issue compromises the confidentiality, integrity and availability of the whole XWiki installation.

To reproduce, on an instance where the CommonMark Markdown Syntax 1.2 extension is installed, log in as a user without script rights. Edit a document and set its syntax to Markdown. Then , add the content `<script>alert("XSS")</script>` and refresh the page. If an alert appears containing "XSS", then the instance is vulnerable.

### Patches
This has been patched in version 8.9 of the CommonMark Markdown Syntax 1.2 extension.

### Workarounds
We're not aware of any workaround except upgrading.

### References
* https://jira.xwiki.org/browse/MARKDOWN-80
* https://github.com/xwiki-contrib/syntax-markdown/commit/d136472d6e8a47981a0ede420a9096f88ffa5035

## References
- https://github.com/xwiki-contrib/syntax-markdown/security/advisories/GHSA-8g2j-rhfh-hq3r
- https://nvd.nist.gov/vuln/detail/CVE-2025-46558
- https://github.com/xwiki-contrib/syntax-markdown/commit/d136472d6e8a47981a0ede420a9096f88ffa5035
- https://github.com/xwiki-contrib/syntax-markdown
- https://jira.xwiki.org/browse/MARKDOWN-80
