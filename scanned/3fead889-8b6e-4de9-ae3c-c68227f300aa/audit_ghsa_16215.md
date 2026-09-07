# [M] CKEditor cross-site scripting vulnerability in AJAX sample

## Summary
Severity: Medium
Advisory: GHSA-wh5w-82f3-wrxh
CVE: CVE-2023-4771
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-07
Source: https://github.com/advisories/GHSA-wh5w-82f3-wrxh
Type: github-advisory

## Affected
- npm: `ckeditor4` — affected >=0 <4.24.0-lts

## Details
### Affected packages
The vulnerability has been discovered in the AJAX sample available at the `samples/old/ajax.html` file location. All integrators that use that sample in the production code can be affected.

### Impact

A potential vulnerability has been discovered in one of CKEditor's 4 samples that are shipped with production code. The vulnerability allowed to execute JavaScript code by abusing the AJAX sample. It affects all users using the CKEditor 4 at version < 4.24.0-lts where `samples/old/ajax.html` is used in a production environment.

### Patches
The problem has been recognized and patched. The fix will be available in version 4.24.0-lts.

### For more information
Email us at [security@cksource.com](mailto:security@cksource.com) if you have any questions or comments about this advisory.

### Acknowledgements
The CKEditor 4 team would like to thank Rafael Pedrero and INCIBE ([original report](https://www.incibe.es/en/incibe-cert/notices/aviso/cross-site-scripting-vulnerability-cksource-ckeditor)) for recognizing and reporting this vulnerability.

## References
- https://github.com/ckeditor/ckeditor4/security/advisories/GHSA-wh5w-82f3-wrxh
- https://nvd.nist.gov/vuln/detail/CVE-2023-4771
- https://github.com/ckeditor/ckeditor4/commit/8ed1a3c93d0ae5f49f4ecff5738ab8a2972194cb
- https://github.com/ckeditor/ckeditor4
- https://www.incibe.es/en/incibe-cert/notices/aviso/cross-site-scripting-vulnerability-cksource-ckeditor
