# [C] Prototype Pollution in ali-security/mongoose

## Summary
Severity: Critical
Advisory: GHSA-rc4v-99cr-pjcm
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:H (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-rc4v-99cr-pjcm
Type: github-advisory

## Affected
- npm: `@seal-security/mongoose-fixed` — affected >=5.3.3 <5.3.4

## Details
### Impact
This vulnerability causes a Prototype Pollution in document.js, through functions such as findByIdAndUpdate().
For applications using Express and EJS, this can potentially allow remote code execution.

### Patches
The original patched version for mongoose 5.3.3 did not include a fix for CVE-2023-3696. Therefore the existing version @seal-security/mongoose-fixed version 5.3.3 is affected by this vulnerability (though it is protected from CVE-2022-2564 and CVE-2019-17426). To mitigate this issue, a @seal-security/mongoose-fixed version 5.3.4 has been deployed. Note that this version is compatible with the original mongoose version 5.3.3, not version 5.3.4

### References
https://security.snyk.io/vuln/SNYK-JS-MONGOOSE-5777721
https://github.com/advisories/GHSA-9m93-w8w6-76hh
https://github.com/Automattic/mongoose/commit/f1efabf350522257364aa5c2cb36e441cf08f1a2

## References
- https://github.com/ali-security/mongoose/security/advisories/GHSA-rc4v-99cr-pjcm
- https://github.com/Automattic/mongoose/commit/f1efabf350522257364aa5c2cb36e441cf08f1a2
- https://github.com/ali-security/mongoose
- https://security.snyk.io/vuln/SNYK-JS-MONGOOSE-5777721
