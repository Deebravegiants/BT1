# [M] HAX CMS application pages vulnerable to clickjacking

## Summary
Severity: Medium
Advisory: GHSA-54vw-f4xf-f92j
CVE: CVE-2025-54139
CWE: CWE-1021
Ecosystem: Packagist, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-07-21
Source: https://github.com/advisories/GHSA-54vw-f4xf-f92j
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=0 <11.0.13
- Packagist: `elmsln/haxcms` — affected >=0 <11.0.8

## Details
### Summary

All pages within the HAX CMS application do not contain headers to stop other websites from loading the site within an iframe. This applies to both the CMS and generated sites.

### PoC

To replicate this vulnerability, load the target page in an iframe and observe the rendered content.

![image](https://github.com/user-attachments/assets/84526738-7101-4842-9bac-d33a41091600)


### Impact

An unauthenticated attacker can load the standalone login page or other sensitive functionality within an iframe, performing a UI redressing attack (Clickjacking). This can be used to perform social engineering attacks to attempt to coerce users into performing unintended actions within the HAX CMS application.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-54vw-f4xf-f92j
- https://nvd.nist.gov/vuln/detail/CVE-2025-54139
- https://github.com/haxtheweb/haxcms-nodejs/commit/777f9a7ff9675a160496f350d766df1f1f9b9b99
- https://github.com/haxtheweb/haxcms-php/commit/708dc8518928fe307044e67bff8b0f397cfdd606
- https://github.com/haxtheweb/issues
