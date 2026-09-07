# [H] Cross-Site Scripting in vant

## Summary
Severity: High
Advisory: GHSA-9xr8-8hmc-389f
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2019-11-22
Source: https://github.com/advisories/GHSA-9xr8-8hmc-389f
Type: github-advisory

## Affected
- npm: `vant` — affected >=0 <2.1.8

## Details
Versions of `vant` prior to 2.1.8 are vulnerable to Cross-Site Scripting. The text value of the `Picker` component column is not sanitized, which may allow attackers to execute arbitrary JavaScript in a victim's browser.


## Recommendation

Upgrade to version 2.1.8 or later.

## References
- https://github.com/youzan/vant/issues/4270
- https://github.com/youzan/vant/pull/4278/commits/d777b78c7dc2c904f474d057ea88449cfe2ca13a
- https://snyk.io/vuln/SNYK-JS-VANT-460461
- https://www.npmjs.com/advisories/1157
