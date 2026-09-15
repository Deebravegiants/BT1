# [M] Contao is vulnerable to remote code execution in template closures

## Summary
Severity: Medium
Advisory: GHSA-98vj-mm79-v77r
CVE: CVE-2025-65960
CWE: CWE-351
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-98vj-mm79-v77r
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=4.0.0 <4.13.57
- Packagist: `contao/core-bundle` — affected >=5.0.0-RC1 <5.3.42
- Packagist: `contao/core-bundle` — affected >=5.4.0-RC1 <5.6.5

## Details
### Impact

Backend users with precise control over the contents of template closures can execute arbitrary PHP functions that do not have required parameters.

### Patches

Update to Contao 4.13.57, 5.3.42 or 5.6.5

### Workarounds

Manually patch the `Contao\Template::once()` method.

### Resources

https://contao.org/en/security-advisories/remote-code-execution-in-template-closures

## References
- https://github.com/contao/contao/security/advisories/GHSA-98vj-mm79-v77r
- https://nvd.nist.gov/vuln/detail/CVE-2025-65960
- https://github.com/contao/contao/commit/577d7fdd5b1ca84f65f034ff556865422f0a3bd1
- https://github.com/contao/contao/commit/676f0855d39007ac9a0dbe7ae6a7414cba2312a5
- https://github.com/contao/contao/commit/ebf84c90e5679a67060f396b924ce4a3c3f206b3
- https://contao.org/en/security-advisories/remote-code-execution-in-template-closures
- https://github.com/contao/contao
