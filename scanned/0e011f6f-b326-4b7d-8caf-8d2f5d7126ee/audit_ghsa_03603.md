# [M] Cross-Site Scripting in iobroker.web

## Summary
Severity: Medium
Advisory: GHSA-6rjc-4pwr-3vp7
CVE: CVE-2019-10771
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-6rjc-4pwr-3vp7
Type: github-advisory

## Affected
- npm: `iobroker.web` — affected >=0 <2.4.10

## Details
Versions of `iobroker.web` prior to 2.4.10 are vulnerable to Cross-Site Scripting. The package fails to escape URL parameters that may be reflected in the server response. This can be used by attackers to execute arbitrary JavaScript in the victim's browser.


## Recommendation

Upgrade to version 2.4.10 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10771
- https://snyk.io/vuln/SNYK-JS-IOBROKERWEB-534971
- https://www.npmjs.com/advisories/1345
