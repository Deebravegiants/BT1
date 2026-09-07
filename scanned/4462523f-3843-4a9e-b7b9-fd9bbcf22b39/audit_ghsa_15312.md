# [H] gettext.js has a Cross-site Scripting injection 

## Summary
Severity: High
Advisory: GHSA-vwhg-jwr4-vxgg
CVE: CVE-2024-43370
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-15
Source: https://github.com/advisories/GHSA-vwhg-jwr4-vxgg
Type: github-advisory

## Affected
- npm: `gettext.js` — affected >=0 <2.0.3

## Details
### Impact
Possible vulnerability to XSS injection if .po dictionary definition files is corrupted

### Patches
Update gettext.js to 2.0.3

### Workarounds
Make sure you control the origin of the definition catalog to prevent the use of this flaw in the definition of plural forms.

## References
- https://github.com/guillaumepotier/gettext.js/security/advisories/GHSA-vwhg-jwr4-vxgg
- https://nvd.nist.gov/vuln/detail/CVE-2024-43370
- https://github.com/guillaumepotier/gettext.js/commit/8150aeba833183e14c2291a8a148b8f79d1d68d8
- https://github.com/guillaumepotier/gettext.js
