# [M] Contao: Insufficient BBCode sanitizer

## Summary
Severity: Medium
Advisory: GHSA-j55w-hjpj-825g
CVE: CVE-2024-28234
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-04-09
Source: https://github.com/advisories/GHSA-j55w-hjpj-825g
Type: github-advisory

## Affected
- Packagist: `contao/comments-bundle` — affected >=2.0.0 <4.13.40
- Packagist: `contao/comments-bundle` — affected >=5.0.0-RC1 <5.3.4

## Details
### Impact

If BBCode is enabled for comments, users can inject CSS styles.

### Patches

Update to Contao 4.13.40 or 5.3.4.

### Workarounds

Disable BBCode for comments.

### References

https://contao.org/en/security-advisories/insufficient-bbcode-sanitization

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-j55w-hjpj-825g
- https://nvd.nist.gov/vuln/detail/CVE-2024-28234
- https://github.com/contao/contao/commit/55b995d8d35da0d36bc6a22c53fe6423ab0c4ae2
- https://github.com/contao/contao/commit/6d42e667177c972ae7c219645593c262d7764ce2
- https://contao.org/en/security-advisories/insufficient-bbcode-sanitization
- https://github.com/contao/contao
