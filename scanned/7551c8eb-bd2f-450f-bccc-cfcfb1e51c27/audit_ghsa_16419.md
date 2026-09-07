# [M] CKEditor4 Cross-site Scripting vulnerability in samples with enabled the preview feature

## Summary
Severity: Medium
Advisory: GHSA-mw2c-vx6j-mg76
CVE: CVE-2024-24816
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-07
Source: https://github.com/advisories/GHSA-mw2c-vx6j-mg76
Type: github-advisory

## Affected
- npm: `ckeditor4` — affected >=0 <4.24.0-lts

## Details
### Affected packages
The vulnerability has been discovered in the samples that use the [preview](https://ckeditor.com/cke4/addon/preview) feature:

* `samples/old/**/*.html`
* `plugins/[plugin name]/samples/**/*.html`

All integrators that use these samples in the production code can be affected.

### Impact

A potential vulnerability has been discovered in one of CKEditor's 4 samples that are shipped with production code. The vulnerability allowed to execute JavaScript code by abusing the misconfigured [preview feature](https://ckeditor.com/cke4/addon/preview). It affects all users using the CKEditor 4 at version < 4.24.0-lts with affected samples used in a production environment.

### Patches
The problem has been recognized and patched. The fix will be available in version 4.24.0-lts.

### For more information
Email us at [security@cksource.com](mailto:security@cksource.com) if you have any questions or comments about this advisory.

### Acknowledgements
The CKEditor 4 team would like to thank [Marcin Wyczechowski](https://www.linkedin.com/in/marcin-wyczechowski-0a823795/) & [Michał Majchrowicz](https://www.linkedin.com/in/micha%C5%82-majchrowicz-mwsc/) [AFINE Team](https://afine.com/) for recognizing and reporting this vulnerability.

## References
- https://github.com/ckeditor/ckeditor4/security/advisories/GHSA-mw2c-vx6j-mg76
- https://nvd.nist.gov/vuln/detail/CVE-2024-24816
- https://github.com/ckeditor/ckeditor4/commit/8ed1a3c93d0ae5f49f4ecff5738ab8a2972194cb
- https://ckeditor.com/cke4/addon/preview
- https://github.com/ckeditor/ckeditor4
