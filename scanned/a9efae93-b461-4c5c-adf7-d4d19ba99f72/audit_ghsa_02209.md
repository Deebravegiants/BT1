# [M] Cross Site Scripting in LavaLite CMS

## Summary
Severity: Medium
Advisory: GHSA-v2f3-f8x4-m3w8
CVE: CVE-2020-23234
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-09
Source: https://github.com/advisories/GHSA-v2f3-f8x4-m3w8
Type: github-advisory

## Affected
- Packagist: `lavalite/cms` — affected >=0

## Details
Cross Site Scripting (XSS) vulnerabiity exists in LavaLite CMS 5.8.0 via the Menu Blocks feature, which can be bypassed by using HTML event handlers, such as "ontoggle,".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-23234
- https://github.com/LavaLite/cms/issues/320
