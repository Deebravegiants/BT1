# [M] Smoothie vulnerable to Cross-site Scripting when tooltipLabel or strokeStyle are controlled by users

## Summary
Severity: Medium
Advisory: GHSA-g662-qq45-ppwm
CVE: CVE-2022-25929
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-21
Source: https://github.com/advisories/GHSA-g662-qq45-ppwm
Type: github-advisory

## Affected
- npm: `smoothie` — affected >=1.31.0 <1.36.1

## Details
The package smoothie from 1.31.0 and before 1.36.1 are vulnerable to Cross-site Scripting (XSS) due to improper user input sanitization in strokeStyle and tooltipLabel properties. Exploiting this vulnerability is possible when the user can control these properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25929
- https://github.com/joewalnes/smoothie/pull/147
- https://github.com/joewalnes/smoothie/commit/8e0920d50da82f4b6e605d56f41b69fbb9606a98
- https://github.com/joewalnes/smoothie
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARS-3177369
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-3177368
- https://security.snyk.io/vuln/SNYK-JS-SMOOTHIE-3177364
