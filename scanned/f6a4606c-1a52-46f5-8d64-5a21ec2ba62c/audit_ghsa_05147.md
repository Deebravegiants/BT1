# [C] xwiki-pro-macros has remote code execution from page title and content via excerpt-include macro

## Summary
Severity: Critical
Advisory: GHSA-w56x-9778-rppx
CVE: CVE-2026-44179
CWE: CWE-95
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-w56x-9778-rppx
Type: github-advisory

## Affected
- Maven: `com.xwiki.pro:xwiki-pro-macros` — affected >=1.13 <1.14.5

## Details
### Summary
The excerpt-include macro does not properly escape the title of the included page and executes the content of the excerpt with the macro's rights. Therefore, it is vulnerable to XWiki syntax injection via the included page's title and content, allowing remote code execution for any user who can edit a page.

### Details
The title of the included page isn't escaped in [ExcerptInclude.xml#L277](https://github.com/xwikisas/xwiki-pro-macros/blob/main/xwiki-pro-macros-ui/src/main/resources/Confluence/Macros/ExcerptInclude.xml#L277). Further, the content of the excerpt macro is rendered to XWiki syntax and output into the macro's content such that it is executed with the macro's rights.

### PoC
1. As a user without script or programming right, create a page named `Exploit`.
2. In the edit screen, change the title to `{{async}}{{groovy}}println("Hello from Groovy Title!"){{/groovy}}{{/async}}`.
3. Set the content to
```
{{excerpt-include 0="Exploit.WebHome"}}{{/excerpt-include}}

{{excerpt}}
  {{async}}{{groovy}}println("Hello from Groovy content!"){{/groovy}}{{/async}}
{{/excerpt}}
```
4. Save and view the page.
5. If this displays "Hello from Groovy Title!" without the surrounding macro code or "Hello from Groovy content!", the attack succeeded.

### Impact
Remote code execution impacts the confidentiality, integrity and availability of the whole XWiki installation.

## References
- https://github.com/xwikisas/xwiki-pro-macros/security/advisories/GHSA-w56x-9778-rppx
- https://github.com/xwikisas/xwiki-pro-macros
