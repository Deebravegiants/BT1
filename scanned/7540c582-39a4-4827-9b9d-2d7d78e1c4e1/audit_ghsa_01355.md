# [M] User Impersonation in converse.js

## Summary
Severity: Medium
Advisory: GHSA-w973-2qcc-p78x
CVE: CVE-2017-5858
CWE: CWE-20, CWE-346
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-w973-2qcc-p78x
Type: github-advisory

## Affected
- npm: `converse.js` — affected >=0 <1.0.7
- npm: `converse.js` — affected >=2.0.0 <2.0.5

## Details
Versions of `converse.js` prior to 1.0.7 for 1.x or 2.0.5 for 2.x are vulnerable to User Impersonation. The package provides an incorrect implementation of [XEP-0280: Message Carbons](https://xmpp.org/extensions/xep-0280.html) that allows a remote attacker to impersonate any user, including contacts, in the vulnerable application's display. This allows for various kinds of social engineering attacks.


## Recommendation

If you're using `converse.js` 1.x, upgrade to 1.0.7 or later.
If you're using `converse.js` 2.x, upgrade to 2.0.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5858
- https://github.com/jcbrand/converse.js/commit/42f249cabbbf5c026398e6d3b350f6f9536ea572
- https://github.com/jcbrand/converse.js
- https://rt-solutions.de/en/2017/02/CVE-2017-5589_xmpp_carbons
- https://rt-solutions.de/wp-content/uploads/2017/02/CVE-2017-5589_xmpp_carbons.pdf
- https://snyk.io/vuln/SNYK-JS-CONVERSEJS-449664
- https://www.npmjs.com/advisories/974
- https://www.openwall.com/lists/oss-security/2017/02/09/29
- http://openwall.com/lists/oss-security/2017/02/09/29
- http://www.securityfocus.com/bid/96183
