# [M] Potential Cross-site Scripting vulnerability in Hydrogen

## Summary
Severity: Medium
Advisory: GHSA-6j22-wv8g-894f
CVE: CVE-2022-29230
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-19
Source: https://github.com/advisories/GHSA-6j22-wv8g-894f
Type: github-advisory

## Affected
- npm: `@shopify/hydrogen` — affected >=0.10.0 <0.19.0

## Details
### Impact
There is a potential Cross-Site Scripting (XSS) vulnerability where an arbitrary user is able to execute scripts on pages that are built with Hydrogen. This affects all versions of Hydrogen starting from version 0.10.0 to 0.18.0. This vulnerability is exploitable in applications whose hydrating data is user controlled. 

### Patches
All Hydrogen users should upgrade their project to v0.19.0.

### Workarounds
There is no current workaround, and users should update as soon as possible.

Additionally, the Content Security Policy is not an effective mitigation for this vulnerability. 

### References
GitHub: [Hydrogen v0.19.0](https://github.com/Shopify/hydrogen/releases/tag/%40shopify/hydrogen%400.19.0)
Fix PR: https://github.com/Shopify/hydrogen/pull/1272

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Shopify/hydrogen](https://github.com/Shopify/hydrogen/issues/new/choose)

## References
- https://github.com/Shopify/hydrogen/security/advisories/GHSA-6j22-wv8g-894f
- https://nvd.nist.gov/vuln/detail/CVE-2022-29230
- https://github.com/Shopify/hydrogen/pull/1272
- https://github.com/Shopify/hydrogen
- https://github.com/Shopify/hydrogen/releases/tag/%40shopify/hydrogen%400.19.0
