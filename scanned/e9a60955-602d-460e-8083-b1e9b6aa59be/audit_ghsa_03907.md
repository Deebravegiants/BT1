# [H] Denial of Service and Content Injection in i18n-node-angular

## Summary
Severity: High
Advisory: GHSA-97gv-3p2c-xw7j
CVE: CVE-2016-10524
CWE: CWE-400, CWE-74
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-97gv-3p2c-xw7j
Type: github-advisory

## Affected
- npm: `i18n-node-angular` — affected >=0 <1.4.0

## Details
Versions of `i18n-node-angular` prior to 1.4.0 are affected by denial of service and cross-site scripting vulnerabilities. The vulnerabilities exist in a REST endpoint that was created for development purposes, but was not disabled in production in affected versions.


## Recommendation

Update to version 1.4.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10524
- https://github.com/oliversalzburg/i18n-node-angular/commit/877720d2d9bb90dc8233706e81ffa03f99fc9dc8
- https://github.com/advisories/GHSA-97gv-3p2c-xw7j
- https://github.com/oliversalzburg/i18n-node-angular
- https://www.npmjs.com/advisories/80
