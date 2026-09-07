# [M] Regular expression Denial of Service in multiple packages

## Summary
Severity: Medium
Advisory: GHSA-3rh3-wfr4-76mj
CVE: CVE-2021-21391
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-04-06
Source: https://github.com/advisories/GHSA-3rh3-wfr4-76mj
Type: github-advisory

## Affected
- npm: `@ckeditor/ckeditor5-engine` — affected >=0 <27.0.0
- npm: `@ckeditor/ckeditor5-font` — affected >=0 <27.0.0
- npm: `@ckeditor/ckeditor5-image` — affected >=0 <27.0.0
- npm: `@ckeditor/ckeditor5-list` — affected >=0 <27.0.0
- npm: `@ckeditor/ckeditor5-markdown-gfm` — affected >=0 <27.0.0
- npm: `@ckeditor/ckeditor5-media-embed` — affected >=0 <27.0.0
- npm: `@ckeditor/ckeditor5-paste-from-office` — affected >=0 <27.0.0
- npm: `@ckeditor/ckeditor5-widget` — affected >=0 <27.0.0

## Details
### Impact
A regular expression denial of service (ReDoS) vulnerability has been discovered in multiple CKEditor 5 packages. The vulnerability allowed to abuse particular regular expressions, which could cause a significant performance drop resulting in a browser tab freeze. It affects all users using the CKEditor 5 packages listed above at version <= 26.0.0.

### Patches
The problem has been recognized and patched. The fix will be available in version 27.0.0.

### For more information
Email us at security@cksource.com if you have any questions or comments about this advisory.

### Acknowledgements
The CKEditor 5 team would like to thank Yeting Li for recognizing and reporting these vulnerabilities.

## References
- https://github.com/ckeditor/ckeditor5/security/advisories/GHSA-3rh3-wfr4-76mj
- https://nvd.nist.gov/vuln/detail/CVE-2021-21391
- https://github.com/ckeditor/ckeditor5/releases/tag/v27.0.0
- https://www.npmjs.com/package/@ckeditor/ckeditor5-engine
- https://www.npmjs.com/package/@ckeditor/ckeditor5-font
- https://www.npmjs.com/package/@ckeditor/ckeditor5-image
- https://www.npmjs.com/package/@ckeditor/ckeditor5-list
- https://www.npmjs.com/package/@ckeditor/ckeditor5-markdown-gfm
- https://www.npmjs.com/package/@ckeditor/ckeditor5-media-embed
- https://www.npmjs.com/package/@ckeditor/ckeditor5-paste-from-office
- https://www.npmjs.com/package/@ckeditor/ckeditor5-widget
