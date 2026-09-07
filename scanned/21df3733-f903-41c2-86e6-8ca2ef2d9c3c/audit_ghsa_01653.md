# [M] AngularJS Cross-site Scripting due to failure to sanitize `xlink.href` attributes

## Summary
Severity: Medium
Advisory: GHSA-r5fx-8r73-v86c
CVE: CVE-2019-14863
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-02-14
Source: https://github.com/advisories/GHSA-r5fx-8r73-v86c
Type: github-advisory

## Affected
- npm: `angular` — affected >=0 <1.5.0-beta.1

## Details
Versions of `angular` prior to 1.5.0-beta.1 are vulnerable to Cross-Site Scripting. The package fails to sanitize `xlink:href` attributes, which may allow attackers to execute arbitrary JavaScript in a victim's browser if the value is user-controlled.


## Recommendation

Upgrade to version 1.5.0-beta.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14863
- https://github.com/angular/angular.js/pull/12524
- https://github.com/angular/angular.js/commit/35a21532b73d5bd84b4325211c563e6a3e2dde82
- https://github.com/angular/angular.js/commit/f33ce173c90736e349cf594df717ae3ee41e0f7a
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14863
- https://github.com/angular/angular.js
- https://snyk.io/vuln/npm:angular:20150807
- https://www.npmjs.com/advisories/1453
