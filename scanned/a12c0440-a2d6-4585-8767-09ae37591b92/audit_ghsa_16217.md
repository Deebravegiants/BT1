# [M] CKEditor4 Cross-site Scripting vulnerability caused by incorrect CDATA detection

## Summary
Severity: Medium
Advisory: GHSA-fq6h-4g8v-qqvm
CVE: CVE-2024-24815
CWE: CWE-79
Ecosystem: Packagist, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-07
Source: https://github.com/advisories/GHSA-fq6h-4g8v-qqvm
Type: github-advisory

## Affected
- npm: `ckeditor4` — affected >=0 <4.24.0-lts
- Packagist: `ckeditor/ckeditor` — affected >=0 <4.24.0

## Details
### Affected packages
The vulnerability has been discovered in the core HTML parsing module and may affect all editor instances that:
* Enabled [full-page editing](https://ckeditor.com/docs/ckeditor4/latest/features/fullpage.html) mode,
* or enabled [CDATA](https://ckeditor.com/docs/ckeditor4/latest/api/CKEDITOR_dtd.html#property-S-cdata) elements in [Advanced Content Filtering](https://ckeditor.com/docs/ckeditor4/latest/guide/dev_advanced_content_filter.html) configuration (defaults to `script` and `style` elements).

### Impact

A potential vulnerability has been discovered in CKEditor 4 HTML processing core module. The vulnerability allowed to inject malformed HTML content bypassing Advanced Content Filtering mechanism, which could result in executing JavaScript code. An attacker could abuse faulty CDATA content detection and use it to prepare an intentional attack on the editor. It affects all users using the CKEditor 4 at version < 4.24.0-lts.

### Patches
The problem has been recognized and patched. The fix will be available in version 4.24.0-lts.

### For more information
Email us at [security@cksource.com](mailto:security@cksource.com) if you have any questions or comments about this advisory.

### Acknowledgements
The CKEditor 4 team would like to thank [Michal Frýba](https://cz.linkedin.com/in/michal-fryba) from [ALEF NULA](https://www.alefnula.com/) for recognizing and reporting this vulnerability.

## References
- https://github.com/ckeditor/ckeditor4/security/advisories/GHSA-fq6h-4g8v-qqvm
- https://nvd.nist.gov/vuln/detail/CVE-2024-24815
- https://github.com/ckeditor/ckeditor4/commit/8ed1a3c93d0ae5f49f4ecff5738ab8a2972194cb
- https://ckeditor.com/docs/ckeditor4/latest/api/CKEDITOR_dtd.html#property-S-cdata
- https://ckeditor.com/docs/ckeditor4/latest/features/fullpage.html
- https://ckeditor.com/docs/ckeditor4/latest/guide/dev_advanced_content_filter.html
- https://github.com/ckeditor/ckeditor4
- https://www.drupal.org/sa-contrib-2024-009
