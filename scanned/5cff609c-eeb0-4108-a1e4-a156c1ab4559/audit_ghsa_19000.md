# [H] Validator is Vulnerable to Incomplete Filtering of One or More Instances of Special Elements

## Summary
Severity: High
Advisory: GHSA-vghf-hv5q-vc2g
CVE: CVE-2025-12758
CWE: CWE-172, CWE-792
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-27
Source: https://github.com/advisories/GHSA-vghf-hv5q-vc2g
Type: github-advisory

## Affected
- npm: `validator` — affected >=0 <13.15.22

## Details
Versions of the package validator before 13.15.22 are vulnerable to Incomplete Filtering of One or More Instances of Special Elements in the isLength() function that does not take into account Unicode variation selectors (\uFE0F, \uFE0E) appearing in a sequence which lead to improper string length calculation. This can lead to an application using isLength for input validation accepting strings significantly longer than intended, resulting in issues like data truncation in databases, buffer overflows in other system components, or denial-of-service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12758
- https://github.com/validatorjs/validator.js/pull/2616
- https://github.com/validatorjs/validator.js/commit/d457ecaf55b0f3d8bd379d82757425d0d13dd382
- https://gist.github.com/koral--/ad31208b25b9e3d1e2e35f1d4d72572e
- https://github.com/validatorjs/validator.js
- https://security.snyk.io/vuln/SNYK-JS-VALIDATOR-13653476
- http://seclists.org/fulldisclosure/2026/Jan/27
