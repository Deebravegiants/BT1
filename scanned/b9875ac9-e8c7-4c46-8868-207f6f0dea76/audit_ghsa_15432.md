# [M] CKEditor4 low-risk cross-site scripting (XSS) vulnerability linked to potential domain takeover

## Summary
Severity: Medium
Advisory: GHSA-6v96-m24v-f58j
CVE: CVE-2024-43411
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-21
Source: https://github.com/advisories/GHSA-6v96-m24v-f58j
Type: github-advisory

## Affected
- npm: `ckeditor4` — affected >=4.22.0 <4.25.0

## Details
### Affected Packages

The issue impacts only editor instances with enabled [version notifications](https://ckeditor.com/docs/ckeditor4/latest/api/CKEDITOR_config.html#cfg-versionCheck).

Please note that this feature is disabled by default in all CKEditor 4 LTS versions. Therefore, if you use CKEditor 4 LTS, it is highly unlikely that you are affected by this vulnerability. If you are unsure, please [contact us](mailto:security@cksource.com).

### Impact

A theoretical vulnerability has been identified in CKEditor 4.22 (and above). In a highly unlikely scenario where an attacker gains control over the https://cke4.ckeditor.com domain, they could potentially execute an attack on CKEditor 4 instances. Although the vulnerability is purely hypothetical, we have addressed it in CKEditor 4.25.0-lts to ensure compliance with security best practices.

### Patches

The issue has been recognized and patched. The fix is available in version 4.25.0-lts.

### For More Information

If you have any questions or comments about this advisory, please email us at [security@cksource.com](mailto:security@cksource.com).

## References
- https://github.com/ckeditor/ckeditor4/security/advisories/GHSA-6v96-m24v-f58j
- https://nvd.nist.gov/vuln/detail/CVE-2024-43411
- https://github.com/ckeditor/ckeditor4/commit/b5069c9cb769ea22eae1cbd7200f22b1cf2e3a7f
- https://github.com/ckeditor/ckeditor4
