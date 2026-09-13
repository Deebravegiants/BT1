# [H] Widget feature vulnerability allowing to execute JavaScript code using undo functionality

## Summary
Severity: High
Advisory: GHSA-6226-h7ff-ch6c
CVE: CVE-2021-32808
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2021-08-23
Source: https://github.com/advisories/GHSA-6226-h7ff-ch6c
Type: github-advisory

## Affected
- npm: `ckeditor4` — affected >=4.13.0 <4.16.2

## Details
### Affected packages
The vulnerability has been discovered in [Widget](https://ckeditor.com/cke4/addon/clipboard) plugin if used alongside [Undo](https://ckeditor.com/cke4/addon/undo) feature.

### Impact
A potential vulnerability has been discovered in CKEditor 4 [Widget](https://ckeditor.com/cke4/addon/widget) package. The vulnerability allowed to abuse undo functionality using malformed widget HTML, which could result in executing JavaScript code. It affects all users using the CKEditor 4 plugins listed above at version >= 4.13.0.

### Patches
The problem has been recognized and patched. The fix will be available in version 4.16.2.

### For more information
Email us at security@cksource.com if you have any questions or comments about this advisory.

### Acknowledgements
The CKEditor 4 team would like to thank Anton Subbotin ([skavans](https://github.com/skavans)) for recognizing and reporting this vulnerability.

## References
- https://github.com/ckeditor/ckeditor4/security/advisories/GHSA-6226-h7ff-ch6c
- https://nvd.nist.gov/vuln/detail/CVE-2021-32808
- https://github.com/ckeditor/ckeditor4
- https://github.com/ckeditor/ckeditor4/releases/tag/4.16.2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NYA354LJP47KCVJMTUO77ZCX3ZK42G3T
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UVOYN2WKDPLKCNILIGEZM236ABQASLGW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WAGNWHFIQAVCP537KFFS2A2GDG66J7XD
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
