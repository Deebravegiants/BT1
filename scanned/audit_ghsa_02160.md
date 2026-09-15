# [M] Clipboard feature vulnerability allowing to inject arbitrary HTML into the editor using paste functionality

## Summary
Severity: Medium
Advisory: GHSA-7889-rm5j-hpgg
CVE: CVE-2021-32809
CWE: CWE-79, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-23
Source: https://github.com/advisories/GHSA-7889-rm5j-hpgg
Type: github-advisory

## Affected
- npm: `ckeditor4` — affected >=4.5.2 <4.16.2

## Details
### Affected packages
The vulnerability has been discovered in [clipboard](https://ckeditor.com/cke4/addon/clipboard) plugin. All plugins with [clipboard](https://ckeditor.com/cke4/addon/clipboard) plugin dependency are affected:

* [clipboard](https://ckeditor.com/cke4/addon/clipboard)
* [pastetext](https://ckeditor.com/cke4/addon/pastetext)
* [pastetools](https://ckeditor.com/cke4/addon/pastetools)
* [widget](https://ckeditor.com/cke4/addon/widget)
* [uploadwidget](https://ckeditor.com/cke4/addon/uploadwidget)
* [autolink](https://ckeditor.com/cke4/addon/autolink)
* [tableselection](https://ckeditor.com/cke4/addon/tableselection)

### Impact
A potential vulnerability has been discovered in CKEditor 4 [Clipboard](https://ckeditor.com/cke4/addon/clipboard) package. The vulnerability allowed to abuse paste functionality using malformed HTML, which could result in injecting arbitrary HTML into the editor. It affects all users using the CKEditor 4 plugins listed above at version >= 4.5.2.

### Patches
The problem has been recognized and patched. The fix will be available in version 4.16.2.

### For more information
Email us at security@cksource.com if you have any questions or comments about this advisory.

### Acknowledgements
The CKEditor 4 team would like to thank Anton Subbotin ([skavans](https://github.com/skavans)) for recognizing and reporting this vulnerability.

## References
- https://github.com/ckeditor/ckeditor4/security/advisories/GHSA-7889-rm5j-hpgg
- https://nvd.nist.gov/vuln/detail/CVE-2021-32809
- https://github.com/ckeditor/ckeditor4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NYA354LJP47KCVJMTUO77ZCX3ZK42G3T
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UVOYN2WKDPLKCNILIGEZM236ABQASLGW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WAGNWHFIQAVCP537KFFS2A2GDG66J7XD
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
