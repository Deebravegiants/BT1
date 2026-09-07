# [H] Fake objects feature vulnerability allowing to execute JavaScript code using malformed HTML.

## Summary
Severity: High
Advisory: GHSA-m94c-37g6-cjhc
CVE: CVE-2021-37695
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-08-23
Source: https://github.com/advisories/GHSA-m94c-37g6-cjhc
Type: github-advisory

## Affected
- npm: `ckeditor4` — affected >=0 <4.16.2

## Details
### Affected packages
The vulnerability has been discovered in [Fake Objects](https://ckeditor.com/cke4/addon/fakeobjects) plugin. All plugins with [Fake Objects](https://ckeditor.com/cke4/addon/fakeobjects) plugin dependency are affected:

* [Fake Objects](https://ckeditor.com/cke4/addon/fakeobjects)
* [Link](https://ckeditor.com/cke4/addon/link)
* [Flash](https://ckeditor.com/cke4/addon/flash)
* [Iframe](https://ckeditor.com/cke4/addon/iframe)
* [Forms](https://ckeditor.com/cke4/addon/forms)
* [Page Break](https://ckeditor.com/cke4/addon/pagebreak)

### Impact
A potential vulnerability has been discovered in CKEditor 4 [Fake Objects](https://ckeditor.com/cke4/addon/fakeobjects) package. The vulnerability allowed to inject malformed Fake Objects HTML, which could result in executing JavaScript code. It affects all users using the CKEditor 4 plugins listed above at version < 4.16.2.

### Patches
The problem has been recognized and patched. The fix will be available in version 4.16.2.

### For more information
Email us at security@cksource.com if you have any questions or comments about this advisory.

### Acknowledgements
The CKEditor 4 team would like to thank Mika Kulmala ([kulmik](https://github.com/kulmik)) for recognizing and reporting this vulnerability.

## References
- https://github.com/ckeditor/ckeditor4/security/advisories/GHSA-m94c-37g6-cjhc
- https://nvd.nist.gov/vuln/detail/CVE-2021-37695
- https://github.com/ckeditor/ckeditor4/commit/de3c001540715f9c3801aaa38a1917de46cfcf58
- https://github.com/ckeditor/ckeditor4
- https://lists.debian.org/debian-lts-announce/2021/11/msg00007.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NYA354LJP47KCVJMTUO77ZCX3ZK42G3T
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UVOYN2WKDPLKCNILIGEZM236ABQASLGW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WAGNWHFIQAVCP537KFFS2A2GDG66J7XD
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
