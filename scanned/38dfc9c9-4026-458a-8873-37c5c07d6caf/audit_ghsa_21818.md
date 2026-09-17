# [C] OS Command Injection in install-package

## Summary
Severity: Critical
Advisory: GHSA-6m4r-m3gc-h4r5
CVE: CVE-2020-7629
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-6m4r-m3gc-h4r5
Type: github-advisory

## Affected
- npm: `install-package` — affected >=0

## Details
install-package through 0.4.0 is vulnerable to Command Injection. It allows execution of arbitrary commands via the options argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7629
- https://github.com/1000ch/install-package/blob/master/index.js#L82
- https://snyk.io/vuln/SNYK-JS-INSTALLPACKAGE-564267
