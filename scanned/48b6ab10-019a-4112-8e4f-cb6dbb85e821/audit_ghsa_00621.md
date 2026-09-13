# [M] Cross-Site Scripting in @risingstack/protect

## Summary
Severity: Medium
Advisory: GHSA-vpch-rxw3-fgx8
CVE: CVE-2018-1000160
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-04-25
Source: https://github.com/advisories/GHSA-vpch-rxw3-fgx8
Type: github-advisory

## Affected
- npm: `@risingstack/protect` — affected >=0

## Details
All versions of `@risingstack/protect` are vulnerable to Cross-Site Scripting. The  `isXss()` XSS validator has several bypasses that may allow attackers to execute arbitrary JavaScript in a victim's browser.


## Recommendation

No fix is currently available. Consider using an alternative package. The package is not actively maintained and will not be patched.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000160
- https://github.com/RisingStack/protect/issues/16
- https://github.com/RisingStack/protect
- https://github.com/RisingStack/protect/blob/60b0c91e86686d34e5202419ce9ae7e8dc08edcd/lib/rules/xss.js#L4-L13
- https://github.com/advisories/GHSA-vpch-rxw3-fgx8
- https://snyk.io/vuln/SNYK-JS-RISINGSTACKPROTECT-455402
- https://www.npmjs.com/advisories/1116
- http://embed.plnkr.co/xHbhB29JWWyMUMeHsLrm
