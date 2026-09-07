# [M] Cross-Site Scripting in status-board

## Summary
Severity: Medium
Advisory: GHSA-6m4r-cgm3-6q7q
CVE: CVE-2019-15478
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-09-23
Source: https://github.com/advisories/GHSA-6m4r-cgm3-6q7q
Type: github-advisory

## Affected
- npm: `status-board` — affected >=0 <1.1.82

## Details
All versions of `status-board` are vulnerable to Cross-Site Scripting. The `renderJsDashboard()` function concatenates the `safeDashboard` variable to the HTTP response message with insufficient sanitization. If this variable is controlled by user input it may allow attackers to execute arbitrary JavaScript in a victim's browser.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15478
- https://github.com/jameswlane/status-board/pull/949
- https://github.com/jameswlane/status-board/pull/949/files
- https://snyk.io/vuln/SNYK-JS-STATUSBOARD-460293
- https://www.npmjs.com/advisories/1151
