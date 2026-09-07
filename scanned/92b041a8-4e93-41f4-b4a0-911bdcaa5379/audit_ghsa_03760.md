# [M] Cross-Site Scripting in cyberchef

## Summary
Severity: Medium
Advisory: GHSA-jp6r-xcjj-5h7r
CVE: CVE-2019-15532
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-08-27
Source: https://github.com/advisories/GHSA-jp6r-xcjj-5h7r
Type: github-advisory

## Affected
- npm: `cyberchef` — affected >=0 <8.31.3

## Details
Versions of `cyberchef` prior to 8.31.3 are vulnerable to Cross-Site Scripting. In `Text Encoding Brute Force` the table rows are created by concatenating the `value` variable unsanitized in the HTML code. If this variable is controlled by user input it allows attackers to execute arbitrary JavaScript in a victim's browser.


## Recommendation

Upgrade to version 8.31.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15532
- https://github.com/gchq/CyberChef/issues/539
- https://github.com/gchq/CyberChef/issues/544
- https://github.com/gchq/CyberChef/commit/01f0625d6a177f9c5df9281f12a27c814c2d8bcf
- https://github.com/gchq/CyberChef/compare/v8.31.1...v8.31.2
- https://snyk.io/vuln/SNYK-JS-CYBERCHEF-460296
- https://www.npmjs.com/advisories/1149
