# [H] Advanced Content Filter (ACF) vulnerability allowing to execute JavaScript code using malformed HTML

## Summary
Severity: High
Advisory: GHSA-pvmx-g8h5-cprj
CVE: CVE-2021-41164
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2021-11-17
Source: https://github.com/advisories/GHSA-pvmx-g8h5-cprj
Type: github-advisory

## Affected
- npm: `ckeditor4` — affected >=0 <4.17.0

## Details
### Affected packages
The vulnerability has been discovered in the Advanced Content Filter (ACF) module and may affect all plugins used by CKEditor 4.

### Impact
A potential vulnerability has been discovered in CKEditor 4 Advanced Content Filter (ACF) core module. The vulnerability allowed to inject malformed HTML bypassing content sanitization, which could result in executing JavaScript code. It affects all users using the CKEditor 4 at version < 4.17.0.

### Patches
The problem has been recognized and patched. The fix will be available in version 4.17.0.

### For more information
Email us at security@cksource.com if you have any questions or comments about this advisory.

### Acknowledgements
The CKEditor 4 team would like to thank Maurice Dauer ([laytonctf](https://twitter.com/laytonctf)) for recognizing and reporting this vulnerability.

## References
- https://github.com/ckeditor/ckeditor4/security/advisories/GHSA-pvmx-g8h5-cprj
- https://nvd.nist.gov/vuln/detail/CVE-2021-41164
- https://github.com/ckeditor/ckeditor4
- https://github.com/ckeditor/ckeditor4/blob/major/CHANGES.md#ckeditor-417
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VR76VBN5GW5QUBJFHVXRX36UZ6YTCMW6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WOZGMCYDB2OKKULFXZKM6V7JJW4ZZHJP
- https://www.drupal.org/sa-core-2021-011
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
