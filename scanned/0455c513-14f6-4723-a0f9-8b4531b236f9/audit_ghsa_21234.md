# [C] js-ini Prorotype Pollution when malicious INI files submitted to an application that parses it with `parse`

## Summary
Severity: Critical
Advisory: GHSA-m939-vrfp-9v8p
CVE: CVE-2020-28461
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-m939-vrfp-9v8p
Type: github-advisory

## Affected
- npm: `js-ini` — affected >=0 <1.3.0

## Details
This affects the package js-ini before 1.3.0. If an attacker submits a malicious INI file to an application that parses it with `parse` , they will pollute the prototype on the application. This can be exploited further depending on the context.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28461
- https://github.com/Sdju/js-ini/commit/fa17efb7e3a7c9464508a254838d4c231784931e
- https://github.com/Sdju/js-ini
- https://security.snyk.io/vuln/SNYK-JS-JSINI-1048970
