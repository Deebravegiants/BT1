# [H] n158 vulnerable to Command Injection due to improper input sanitization in the 'module.exports' function

## Summary
Severity: High
Advisory: GHSA-549h-r7g9-2qpf
CVE: CVE-2023-26127
CWE: CWE-74, CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-27
Source: https://github.com/advisories/GHSA-549h-r7g9-2qpf
Type: github-advisory

## Affected
- npm: `n158` — affected >=0

## Details
All versions of the package n158 are vulnerable to Command Injection due to improper input sanitization in the 'module.exports' function.

**Note:**

To execute the code snippet and potentially exploit the vulnerability, the attacker needs to have the ability to run Node.js code within the target environment. This typically requires some level of access to the system or application hosting the Node.js environment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26127
- https://github.com/dsilva2401/n158
- https://github.com/dsilva2401/n158/blob/master/src/cli/initProject.js#L8
- https://security.snyk.io/vuln/SNYK-JS-N158-3183746
