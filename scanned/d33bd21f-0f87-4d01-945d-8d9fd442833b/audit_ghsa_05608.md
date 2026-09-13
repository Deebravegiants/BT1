# [M] CakePHP PaginatorHelper::limitControl() vulnerable to reflected cross-site-scripting

## Summary
Severity: Medium
Advisory: GHSA-qh8m-9qxx-53m5
CVE: CVE-2026-23643
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-qh8m-9qxx-53m5
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=5.2.10 <5.2.12
- Packagist: `cakephp/cakephp` — affected >=5.3.0 <5.3.1

## Details
### Impact
The `PaginatorHelper::limitControl()` method has a cross-site-scripting vulnerability via query string parameter manipulation.

### Patches
This issue has been fixed in 5.2.12 and 5.3.1

### Workarounds
If you are unable to upgrade, you should avoid using `Paginator::limitControl()` until you can upgrade.

## References
- https://github.com/cakephp/cakephp/security/advisories/GHSA-qh8m-9qxx-53m5
- https://nvd.nist.gov/vuln/detail/CVE-2026-23643
- https://github.com/cakephp/cakephp/issues/19172
- https://github.com/cakephp/cakephp/commit/c842e7f45d85696e6527d8991dd72f525ced955f
- https://bakery.cakephp.org/2026/01/14/cakephp_5212.html
- https://github.com/cakephp/cakephp
- https://github.com/cakephp/cakephp/releases/tag/5.2.12
- https://github.com/cakephp/cakephp/releases/tag/5.3.1
