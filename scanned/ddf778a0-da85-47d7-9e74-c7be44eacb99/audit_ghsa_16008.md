# [M] Slim Select has potential Cross-site Scripting issue

## Summary
Severity: Medium
Advisory: GHSA-qvqv-mcxr-x8qw
CVE: CVE-2024-9440
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-02
Source: https://github.com/advisories/GHSA-qvqv-mcxr-x8qw
Type: github-advisory

## Affected
- npm: `slim-select` — affected >=2.0.0 <2.9.2

## Details
Slim Select 2.0 versions through 2.9.0 are affected by a potential cross-site scripting vulnerability. In select.ts:createOption(), the text variable from the user-provided Options object is assigned to an innerHTML without sanitation. Software that depends on this library to dynamically generate lists using unsanitized user-provided input may be vulnerable to cross-site scripting, resulting in attacker executed JavaScript. This vulnerability is fixed in 2.9.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9440
- https://github.com/brianvoe/slim-select/issues/564
- https://github.com/brianvoe/slim-select/pull/572
- https://github.com/brianvoe/slim-select/commit/f8534f27d6e9bab89024d139f1c4f7555f1efd5e
- https://github.com/brianvoe/slim-select
- https://github.com/brianvoe/slim-select/blob/e7e37e2ff90e125f846bd98d6b8f278524ead79e/src/slim-select/select.ts#L377
- https://vulncheck.com/advisories/slim-select-xss
