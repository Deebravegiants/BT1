# [M] lockfile-lint-api Vulnerable to Incorrect Behavior Order

## Summary
Severity: Medium
Advisory: GHSA-7cfr-5cjf-32p4
CVE: CVE-2025-4759
CWE: CWE-179
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2025-05-16
Source: https://github.com/advisories/GHSA-7cfr-5cjf-32p4
Type: github-advisory

## Affected
- npm: `lockfile-lint-api` — affected >=0 <5.9.2

## Details
Versions of the package lockfile-lint-api before 5.9.2 are vulnerable to Incorrect Behavior Order: Early Validation via the resolved attribute of the package URL validation which can be bypassed by extending the package name allowing an attacker to install other npm packages than the intended one.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4759
- https://github.com/lirantal/lockfile-lint/pull/204
- https://github.com/lirantal/lockfile-lint/commit/9e5305bd3e4f0c6acc0d23ec43eac2bd5303b4ca
- https://gist.github.com/Xavier59/881aef04940970dc3e738dcbff64151f
- https://github.com/lirantal/lockfile-lint
- https://github.com/lirantal/lockfile-lint/blob/89b5cad028df4d77bab2b73ac93bc61e392668ab/packages/lockfile-lint-api/src/validators/ValidatePackageNames.js#L51-L63
- https://security.snyk.io/vuln/SNYK-JS-LOCKFILELINTAPI-10169587
