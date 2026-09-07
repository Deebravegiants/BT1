# [M] Cross-site scripting (XSS) in the CKEditor 5 real-time collaboration package

## Summary
Severity: Medium
Advisory: GHSA-j3mm-wmfm-mwvh
CVE: CVE-2025-25299
CWE: CWE-79, CWE-80
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-02-20
Source: https://github.com/advisories/GHSA-j3mm-wmfm-mwvh
Type: github-advisory

## Affected
- npm: `@ckeditor/ckeditor5-real-time-collaboration` — affected >=41.3.0 <44.2.1
- npm: `ckeditor5-premium-features` — affected >=42.0.0 <44.2.1

## Details
### Impact
During a recent internal audit, we identified a Cross-Site Scripting (XSS) vulnerability in the CKEditor 5 real-time collaboration package. This vulnerability can lead to unauthorized JavaScript code execution and affects user markers, which represent users' positions within the document.

This vulnerability affects only installations with [Real-time collaborative editing](https://ckeditor.com/docs/ckeditor5/latest/features/collaboration/real-time-collaboration/real-time-collaboration.html) enabled.

### Patches
The problem has been recognized and patched. The fix will be available in version 44.2.1 (and above).

### For more information
Email us at [security@cksource.com](mailto:security@cksource.com) if you have any questions or comments about this advisory.

## References
- https://github.com/ckeditor/ckeditor5/security/advisories/GHSA-j3mm-wmfm-mwvh
- https://nvd.nist.gov/vuln/detail/CVE-2025-25299
- https://ckeditor.com/docs/ckeditor5/latest/features/collaboration/real-time-collaboration/real-time-collaboration.html
- https://ckeditor.com/docs/ckeditor5/latest/features/collaboration/real-time-collaboration/real-time-collaboration.html?docId=ee1dca024c9b4e44aef039f99ebe6c664
- https://github.com/ckeditor/ckeditor5
- https://github.com/ckeditor/ckeditor5/releases/tag/v44.2.1
