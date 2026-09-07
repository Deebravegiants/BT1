# [M] TinyMCE vulnerable to mutation Cross-site Scripting via special characters in unescaped text nodes

## Summary
Severity: Medium
Advisory: GHSA-v626-r774-j7f8
CVE: CVE-2023-48219
CWE: CWE-79
Ecosystem: NuGet, Packagist, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-11-15
Source: https://github.com/advisories/GHSA-v626-r774-j7f8
Type: github-advisory

## Affected
- npm: `tinymce` — affected >=0 <5.10.9
- npm: `tinymce` — affected >=6.0.0 <6.7.3
- Packagist: `tinymce/tinymce` — affected >=0 <5.10.9
- Packagist: `tinymce/tinymce` — affected >=6.0.0 <6.7.3
- NuGet: `TinyMCE` — affected >=0 <5.10.9
- NuGet: `TinyMCE` — affected >=6.0.0 <6.7.3

## Details
### Impact
A [mutation cross-site scripting](https://researchgate.net/publication/266654651_mXSS_attacks_Attacking_well-secured_web-applications_by_using_innerHTML_mutations) (mXSS) vulnerability was discovered in TinyMCE’s core undo/redo functionality and other APIs and plugins. Text nodes within specific parents are not escaped upon serialization according to the [HTML standard](https://html.spec.whatwg.org/multipage/parsing.html#serialising-html-fragments). If such text nodes contain a special character reserved as an internal marker, they can be combined with other HTML patterns to form malicious snippets. These snippets pass the initial sanitisation layer when the content is parsed into the editor body, but can trigger XSS when the special internal marker is removed from the content and re-parsed. Such mutations occur when serialised HTML content is processed before being stored in the undo stack, or when the following APIs and plugins are used:
* [`tinymce.Editor.getContent({ format: 'raw' })`](https://tiny.cloud/docs/tinymce/6/apis/tinymce.editor/#getContent)
* [`tinymce.Editor.resetContent()`](https://tiny.cloud/docs/tinymce/6/apis/tinymce.editor/#resetContent)
* [Autosave Plugin](https://tiny.cloud/docs/tinymce/6/autosave/)

### Patches
This vulnerability has been patched in TinyMCE 6.7.3 by:
* ensuring that any unescaped text nodes which contain the special internal marker are emptied before removing the marker from the rest of the HTML, and
* removing the special internal marker from content strings passed to `Editor.setContent`, `Editor.insertContent`, and `Editor.resetContent` APIs to prevent them from being loaded into the editor as user-provided content.

### Fix
To avoid this vulnerability:
- Upgrade to TinyMCE 6.7.3 or higher for TinyMCE 6.x.
- Upgrade to TinyMCE 5.10.9 or higher for TinyMCE 5.x.

### Acknowledgements
Tiny Technologies would like to thank Masato Kinugawa of [Cure53](https://cure53.de/) for discovering this vulnerability.

### References
- [TinyMCE 5.10.9 Release Notes](https://tiny.cloud/docs/release-notes/release-notes5109/)
- [TinyMCE 6.7.3 Release Notes](https://tiny.cloud/docs/tinymce/6/6.7.3-release-notes/)

### For more information

Email us at [infosec@tiny.cloud](mailto:infosec@tiny.cloud)
Open an issue in the [TinyMCE repo](https://github.com/tinymce/tinymce/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc)

## References
- https://github.com/tinymce/tinymce/security/advisories/GHSA-v626-r774-j7f8
- https://nvd.nist.gov/vuln/detail/CVE-2023-48219
- https://github.com/tinymce/tinymce
- https://github.com/tinymce/tinymce/releases/tag/5.10.9
- https://github.com/tinymce/tinymce/releases/tag/6.7.3
- https://tiny.cloud/docs/release-notes/release-notes5109
- https://tiny.cloud/docs/tinymce/6/6.7.3-release-notes
