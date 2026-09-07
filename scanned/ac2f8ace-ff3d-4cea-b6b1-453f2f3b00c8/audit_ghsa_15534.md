# [H] node-gettext vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-g974-hxvm-x689
CVE: CVE-2024-21528
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-09-10
Source: https://github.com/advisories/GHSA-g974-hxvm-x689
Type: github-advisory

## Affected
- npm: `node-gettext` — affected >=0

## Details
All versions of the package node-gettext are vulnerable to Prototype Pollution via the addTranslations() function in gettext.js due to improper user input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21528
- https://github.com/alexanderwallin/node-gettext
- https://github.com/alexanderwallin/node-gettext/blob/65d9670f691c2eeca40dce129c95bcf8b613d344/lib/gettext.js#L113
- https://security.snyk.io/vuln/SNYK-JS-NODEGETTEXT-6100943
