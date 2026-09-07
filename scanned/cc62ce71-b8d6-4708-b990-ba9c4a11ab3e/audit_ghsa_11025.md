# [M] CKEditor 5 has Cross-site Scripting (XSS) in the HTML Support package

## Summary
Severity: Medium
Advisory: GHSA-jrqm-vmqc-gm93
CVE: CVE-2026-28343
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-jrqm-vmqc-gm93
Type: github-advisory

## Affected
- npm: `@ckeditor/ckeditor5-html-support` — affected >=29.0.0 <47.6.0
- npm: `ckeditor5` — affected >=29.0.0 <47.6.0

## Details
### Impact
A Cross-Site Scripting (XSS) vulnerability has been discovered in the General HTML Support feature. This vulnerability could be triggered by inserting specially crafted markup, leading to unauthorized JavaScript code execution, if the editor instance used an unsafe General HTML Support configuration.

This vulnerability affects only installations where the editor configuration meets the following criteria:

* [General HTML Support](https://ckeditor.com/docs/ckeditor5/latest/features/html/general-html-support.html) is enabled,
* General HTML Support configuration allows inserting unsafe markup (see [Security](https://ckeditor.com/docs/ckeditor5/latest/features/html/general-html-support.html#security) section to learn more).

### Patches
The problem has been recognized and patched. The fix will be available in version 47.6.0 (and above).

### Workarounds
CKEditor 5 recommends configuring General HTML Support securely to ensure that unsafe content is not accepted. Please refer to the [Security](https://ckeditor.com/docs/ckeditor5/latest/features/html/general-html-support.html#security) section for detailed guidance.

### Credits
CKEditor 5 would like to thank: 
- Emilio Kevin
- Jeongwoo Lee, Younsoung Kim, Minseok Kim and Jinyeong Kim from ENKI Whitehat

for responsibly reporting this vulnerability.

### For more information
Email us at [security@cksource.com](mailto:security@cksource.com) if you have any questions or comments about this advisory.

## References
- https://github.com/ckeditor/ckeditor5/security/advisories/GHSA-jrqm-vmqc-gm93
- https://nvd.nist.gov/vuln/detail/CVE-2026-28343
- https://github.com/ckeditor/ckeditor5
- https://github.com/ckeditor/ckeditor5/releases/tag/v29.0.0
- https://github.com/ckeditor/ckeditor5/releases/tag/v47.6.0
