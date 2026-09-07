# [M] CKEditor5 cross-site scripting vulnerability caused by the editor instance destroying process

## Summary
Severity: Medium
Advisory: GHSA-42wq-rch8-6f6j
CVE: CVE-2022-31175
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-42wq-rch8-6f6j
Type: github-advisory

## Affected
- npm: `@ckeditor/ckeditor5-markdown-gfm` — affected >=0 <35.0.1
- npm: `@ckeditor/ckeditor5-html-support` — affected >=0 <35.0.1
- npm: `@ckeditor/ckeditor5-html-embed` — affected >=0 <35.0.1

## Details
### Affected packages
@ckeditor/ckeditor5-markdown-gfm
@ckeditor/ckeditor5-html-support
@ckeditor/ckeditor5-html-embed

### Impact
A cross-site scripting vulnerability has been discovered affecting three optional CKEditor 5's packages. The vulnerability allowed to trigger a JavaScript code after fulfilling special conditions:

a) Using one of the affected packages. In case of `ckeditor5-html-support` and `ckeditor5-html-embed`, additionally, it was required to use a configuration that allows unsafe markup inside the editor,
b) Initializing the editor on an element and using an element other than `<textarea>` as a base,
c) Destroying the editor instance.

The root cause of the issue was a mechanism responsible for updating the source element with the markup coming from the CKEditor 5 data pipeline after destroying the editor. 

This vulnerability might affect a small percent of integrators that depend on dynamic editor initialization/destroy and use [Markdown](https://ckeditor.com/docs/ckeditor5/latest/features/markdown.html), [General HTML Support](https://ckeditor.com/docs/ckeditor5/latest/features/general-html-support.html) or [HTML embed](https://ckeditor.com/docs/ckeditor5/latest/features/html-embed.html) features.

### Patches
The problem has been recognized and patched. The fix will be available in version 35.0.1.

### For more information
Email us at [security@cksource.com](mailto:security@cksource.com) if you have any questions or comments about this advisory.

## References
- https://github.com/ckeditor/ckeditor5/security/advisories/GHSA-42wq-rch8-6f6j
- https://nvd.nist.gov/vuln/detail/CVE-2022-31175
- https://ckeditor.com/docs/ckeditor5/latest/features/general-html-support.html
- https://ckeditor.com/docs/ckeditor5/latest/features/html-embed.html
- https://ckeditor.com/docs/ckeditor5/latest/features/markdown.html
- https://github.com/ckeditor/ckeditor5
