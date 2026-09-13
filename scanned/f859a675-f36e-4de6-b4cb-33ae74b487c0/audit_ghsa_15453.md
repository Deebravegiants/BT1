# [M] Contao affected by insert tag injection via canonical URL

## Summary
Severity: Medium
Advisory: GHSA-2xpq-xp6c-5mgj
CVE: CVE-2024-45612
CWE: CWE-20, CWE-74, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-2xpq-xp6c-5mgj
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=4.13.0 <4.13.49
- Packagist: `contao/core-bundle` — affected >=5.0.0 <5.3.15
- Packagist: `contao/core-bundle` — affected >=5.4.0 <5.4.3

## Details
### Impact

It is possible to inject insert tags in canonical URLs which will be replaced when the page is rendered.

### Patches

Update to Contao 4.13.49, 5.3.15 or 5.4.3.

### Workarounds

Disable canonical tags in the settings of the website root page.

### References

https://contao.org/en/security-advisories/insert-tag-injection-via-canonical-urls

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-2xpq-xp6c-5mgj
- https://nvd.nist.gov/vuln/detail/CVE-2024-45612
- https://github.com/contao/contao/commit/1c28e9ac7a7b915134962a59681a8701a44ccbe2
- https://github.com/contao/contao/commit/d105224e14ddc84f27cd8802b553369decdcbe66
- https://github.com/contao/contao/commit/ffe05cda5310dc2bd259d1391197f3849dab8590
- https://contao.org/en/security-advisories/insert-tag-injection-via-canonical-urls
- https://github.com/contao/contao
