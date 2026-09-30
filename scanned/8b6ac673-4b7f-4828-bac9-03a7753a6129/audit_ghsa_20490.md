# [C] Incorrect Authorization in latte/latte

## Summary
Severity: Critical
Advisory: GHSA-6pj2-5fqq-xvjc
CVE: CVE-2021-23803
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-6pj2-5fqq-xvjc
Type: github-advisory

## Affected
- Packagist: `latte/latte` — affected >=0 <2.10.6

## Details
This affects the package latte/latte before 2.10.6. There is a way to bypass allowFunctions that will affect the security of the application. When the template is set to allow/disallow the use of certain functions, adding control characters (x00-x08) after the function will bypass these restrictions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23803
- https://github.com/nette/latte/issues/279
- https://github.com/nette/latte/commit/227c86eda9a8a6d060ea8501923e768b6d992210
- https://github.com/nette/latte
- https://snyk.io/vuln/SNYK-PHP-LATTELATTE-1932226
