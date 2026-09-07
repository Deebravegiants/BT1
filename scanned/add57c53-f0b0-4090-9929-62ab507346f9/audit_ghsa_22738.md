# [C] Fat-Free Framework arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-hpj2-4hfj-g233
CVE: CVE-2020-5203
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hpj2-4hfj-g233
Type: github-advisory

## Affected
- Packagist: `bcosca/fatfree` — affected >=0 <3.7.2

## Details
In Fat-Free Framework 3.7.1, attackers can achieve arbitrary code execution if developers choose to pass user controlled input (e.g., `$_REQUEST`, `$_GET`, or `$_POST`) to the framework's Clear method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5203
- https://github.com/bcosca/fatfree-core/commit/dae95a0baf3963a9ef87c17cee52f78f77e21829
- https://github.com/bcosca/fatfree
- https://github.com/bcosca/fatfree/releases
