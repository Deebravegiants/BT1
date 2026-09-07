# [M] Contao does not properly manage privileges for page and article fields

## Summary
Severity: Medium
Advisory: GHSA-qqfq-7cpp-hcqj
CVE: CVE-2025-57759
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-08-28
Source: https://github.com/advisories/GHSA-qqfq-7cpp-hcqj
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=5.3.0 <5.3.38
- Packagist: `contao/core-bundle` — affected >=5.4.0-RC1 <5.6.1
- Packagist: `contao/contao` — affected >=5.3.0 <5.3.38
- Packagist: `contao/contao` — affected >=5.4.0-RC1 <5.6.1

## Details
### Impact

Under certain conditions, back end users may be able to edit fields of pages and articles without having the necessary permissions.

### Patches

Update to Contao 5.3.38 or 5.6.1.

### Workarounds

None.

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-qqfq-7cpp-hcqj
- https://nvd.nist.gov/vuln/detail/CVE-2025-57759
- https://github.com/contao/contao/commit/80ee7db12d55ad979d9b1b180f273d4e2668851f
- https://contao.org/en/security-advisories/improper-privilege-management-for-page-and-article-fields
- https://github.com/contao/contao
