# [M] Cross-site scripting (XSS) in the clipboard package

## Summary
Severity: Medium
Advisory: GHSA-rgg8-g5x8-wr9v
CVE: CVE-2024-45613
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-09-25
Source: https://github.com/advisories/GHSA-rgg8-g5x8-wr9v
Type: github-advisory

## Affected
- npm: `ckeditor5` — affected >=40.0.0 <43.1.1
- npm: `@ckeditor/ckeditor5-clipboard` — affected >=40.0.0 <43.1.1

## Details
### Impact
During a recent internal audit, we identified a Cross-Site Scripting (XSS) vulnerability in the CKEditor 5 clipboard package. This vulnerability could be triggered by a specific user action, leading to unauthorized JavaScript code execution, if the attacker managed to insert a malicious content into the editor, which might happen with a very specific editor configuration.

This vulnerability affects **only** installations where the editor configuration meets the following criteria:

1. The [**Block Toolbar**](https://ckeditor.com/docs/ckeditor5/latest/getting-started/setup/toolbar.html#block-toolbar) plugin is enabled.
1. One of the following plugins is also enabled:
    - [**General HTML Support**](https://ckeditor.com/docs/ckeditor5/latest/features/html/general-html-support.html) with a configuration that permits unsafe markup.
    - [**HTML Embed**](https://ckeditor.com/docs/ckeditor5/latest/features/html/html-embed.html).

### Patches
The problem has been recognized and patched. The fix will be available in version 43.1.1 (and above), and explicitly in version 41.3.2.

### Workarounds
It's highly recommended to update to the version 43.1.1 or higher. However, if the update is not an option, we recommend disabling the block toolbar plugin.

### For more information
Email us at [security@cksource.com](mailto:security@cksource.com) if you have any questions or comments about this advisory.

## References
- https://github.com/ckeditor/ckeditor5/security/advisories/GHSA-rgg8-g5x8-wr9v
- https://nvd.nist.gov/vuln/detail/CVE-2024-45613
- https://github.com/ckeditor/ckeditor5
- https://github.com/ckeditor/ckeditor5/releases/tag/v43.1.1
