# [M] Cross-Site Scripting in selectize-plugin-a11y

## Summary
Severity: Medium
Advisory: GHSA-8cpw-73f2-w58m
CVE: CVE-2019-15482
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-08-27
Source: https://github.com/advisories/GHSA-8cpw-73f2-w58m
Type: github-advisory

## Affected
- npm: `selectize-plugin-a11y` — affected >=0 <1.1.0

## Details
Versions of `selectize-plugin-a11y ` prior to 1.1.0 are vulnerable to Cross-Site Scripting. The `accessibility.liveRegion.speak` function does not sanitize the `msg` variable before rendering it as HTML. If this variable is controlled by user input it allows attackers to execute arbitrary JavaScript in a victim's browser.


## Recommendation

Upgrade to version 1.1.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15482
- https://github.com/SLMNBJ/selectize-plugin-a11y/pull/9
- https://www.npmjs.com/advisories/1145
- https://www.npmjs.com/package/selectize-plugin-a11y/v/1.1.0
