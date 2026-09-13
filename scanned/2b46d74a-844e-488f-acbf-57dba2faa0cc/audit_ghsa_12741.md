# [C] nemo-appium vulnerable to OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-c6rx-gxqv-vr5j
CVE: CVE-2022-21129
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-31
Source: https://github.com/advisories/GHSA-c6rx-gxqv-vr5j
Type: github-advisory

## Affected
- npm: `nemo-appium` — affected >=0 <0.0.9

## Details
Versions of the package nemo-appium before 0.0.9 are vulnerable to Command Injection due to improper input sanitization in the 'module.exports.setup' function. 

**Note:** In order to exploit this vulnerability appium-running 0.1.3 has to be installed as one of nemo-appium dependencies.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21129
- https://github.com/paypal/nemo-appium/commit/aa271d36dd5c81baae3c43aa2616c84f0ee4195f
- https://github.com/paypal/nemo-appium
- https://github.com/paypal/nemo-appium/blob/master/index.js%23L27
- https://security.snyk.io/vuln/SNYK-JS-NEMOAPPIUM-3183747
