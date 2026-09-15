# [M] Sandbox escape in notevil and argencoders-notevil

## Summary
Severity: Medium
Advisory: GHSA-8g4m-cjm2-96wq
CVE: CVE-2021-23771
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-8g4m-cjm2-96wq
Type: github-advisory

## Affected
- npm: `notevil` — affected >=0
- npm: `argencoders-notevil` — affected >=0

## Details
This affects all versions of package notevil; all versions of package argencoders-notevil. It is vulnerable to Sandbox Escape leading to Prototype pollution. The package fails to restrict access to the main context, allowing an attacker to add or modify an object's prototype. **Note:** This vulnerability derives from an incomplete fix in [SNYK-JS-NOTEVIL-608878](https://security.snyk.io/vuln/SNYK-JS-NOTEVIL-608878). This package has been deprecated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23771
- https://github.com/mmckegg/notevil
- https://snyk.io/vuln/SNYK-JS-ARGENCODERSNOTEVIL-2388587
- https://snyk.io/vuln/SNYK-JS-NOTEVIL-2385946
