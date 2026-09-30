# [H] keep-module-latest vulnerable to Command Injection due to missing input sanitization 

## Summary
Severity: High
Advisory: GHSA-wxrx-pc44-rcgc
CVE: CVE-2023-26128
CWE: CWE-20, CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-27
Source: https://github.com/advisories/GHSA-wxrx-pc44-rcgc
Type: github-advisory

## Affected
- npm: `keep-module-latest` — affected >=0

## Details
All versions of the package keep-module-latest are vulnerable to Command Injection due to missing input sanitization or other checks and sandboxes being employed to the installModule function.

**Note:**

To execute the code snippet and potentially exploit the vulnerability, the attacker needs to have the ability to run Node.js code within the target environment. This typically requires some level of access to the system or application hosting the Node.js environment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26128
- https://github.com/liujunyang/keep-module-latest
- https://github.com/liujunyang/keep-module-latest/blob/master/index.js%23L50
- https://security.snyk.io/vuln/SNYK-JS-KEEPMODULELATEST-3157165
