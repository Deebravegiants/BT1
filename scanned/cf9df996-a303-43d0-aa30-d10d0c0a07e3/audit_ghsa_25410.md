# [M] AntSword RCE and XSS via code injection

## Summary
Severity: Medium
Advisory: GHSA-hq75-ggc3-8h3q
CVE: CVE-2019-13970
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hq75-ggc3-8h3q
Type: github-advisory

## Affected
- npm: `antsword` — affected >=0 <2.1.0

## Details
In antSword before 2.1.0, self-XSS in the database configuration leads to code execution via `modules/database/asp/index.js`, `modules/database/custom/index.js`, `modules/database/index.js`, or `modules/database/php/index.js`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13970
- https://github.com/AntSwordProject/antSword/issues/151
- https://github.com/AntSwordProject/antSword/commit/4b932e81447b4b0475f4fce45525547395c249d3
- https://github.com/AntSwordProject/antSword
- https://github.com/AntSwordProject/antSword/compare/ed01dea...834063a
