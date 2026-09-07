# [H] bwm-ng vulnerable to command injection

## Summary
Severity: High
Advisory: GHSA-8vw3-vxmj-h43w
CVE: CVE-2023-26129
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-27
Source: https://github.com/advisories/GHSA-8vw3-vxmj-h43w
Type: github-advisory

## Affected
- npm: `bwm-ng` — affected >=0

## Details
All versions of the package bwm-ng are vulnerable to Command Injection due to improper input sanitization in the 'check' function in the bwm-ng.js file. 

**Note:**

To execute the code snippet and potentially exploit the vulnerability, the attacker needs to have the ability to run Node.js code within the target environment. This typically requires some level of access to the system or application hosting the Node.js environment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26129
- https://security.snyk.io/vuln/SNYK-JS-BWMNG-3175876
