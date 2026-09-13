# [M] CKEditor 5 Markdown plugin Regular expression Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-hgmg-hhc8-g5wr
CVE: CVE-2021-21254
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-01-29
Source: https://github.com/advisories/GHSA-hgmg-hhc8-g5wr
Type: github-advisory

## Affected
- npm: `@ckeditor/ckeditor5-markdown-gfm` — affected >=0 <25.0.0

## Details
### Impact
A regular expression denial of service (ReDoS) vulnerability has been discovered in the CKEditor 5 Markdown plugin code. The vulnerability allowed to abuse a link recognition regular expression, which could cause a significant performance drop resulting in a browser tab freeze. It affects all users using the CKEditor 5 Markdown plugin at version <= 24.0.0. 

### Patches
The problem has been recognized and patched. The fix will be available in version 25.0.0.

### Workarounds
The user can work around the issue by:
- Upgrading CKEditor 5 to version 25.0.0.
- Disabling the Markdown plugin.

### More information
If you have any questions or comments about this advisory:
* Email us at [security@cksource.com](mailto:security@cksource.com)

### Acknowledgements
The CKEditor 5 team would like to thank Erik Krogh Kristensen from the GitHub team for recognizing this vulnerability and 
Alvaro Muñoz from GitHub for reporting it.

## References
- https://github.com/ckeditor/ckeditor5/security/advisories/GHSA-hgmg-hhc8-g5wr
- https://nvd.nist.gov/vuln/detail/CVE-2021-21254
- https://github.com/ckeditor/ckeditor5
- https://github.com/ckeditor/ckeditor5/releases/tag/v25.0.0
- https://www.npmjs.com/package/@ckeditor/ckeditor5-markdown-gfm
