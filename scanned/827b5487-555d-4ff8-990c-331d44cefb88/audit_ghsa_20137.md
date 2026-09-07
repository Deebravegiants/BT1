# [C] safe-eval vulnerable to Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-33vh-7x8q-mg35
CVE: CVE-2022-25904
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-20
Source: https://github.com/advisories/GHSA-33vh-7x8q-mg35
Type: github-advisory

## Affected
- npm: `safe-eval` — affected >=0

## Details
All versions of package safe-eval are vulnerable to Prototype Pollution which allows an attacker to add or modify properties of the Object.prototype.Consolidate when using the function safeEval. This is because the function uses vm variable, leading an attacker to modify properties of the Object.prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25904
- https://github.com/hacksparrow/safe-eval/issues/26
- https://github.com/hacksparrow/safe-eval
- https://security.snyk.io/vuln/SNYK-JS-SAFEEVAL-3175701
