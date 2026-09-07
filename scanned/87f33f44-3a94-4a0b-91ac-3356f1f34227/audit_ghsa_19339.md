# [M] Symfony UX allows unsanitized HTML attribute injection via ComponentAttributes

## Summary
Severity: Medium
Advisory: GHSA-5j3w-5pcr-f8hg
CVE: CVE-2025-47946
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-05-19
Source: https://github.com/advisories/GHSA-5j3w-5pcr-f8hg
Type: github-advisory

## Affected
- Packagist: `symfony/ux-twig-component` — affected >=0 <2.25.1
- Packagist: `symfony/ux-live-component` — affected >=0 <2.25.1

## Details
### Impact

Rendering `{{ attributes }}` or using any method that returns a `ComponentAttributes` instance (e.g. `only()`, `defaults()`, `without()`) ouputs attribute values directly without escaping. If these values are unsafe (e.g. contain user input), this can lead to HTML attribute injection and XSS vulnerabilities.

### Patches

The issue is fixed in version `2.25.1` of `symfony/ux-twig-component` by using Twig's `EscaperRuntime` to properly escape HTML attributes in `ComponentAttributes`.  If you use `symfony/ux-live-component`, you must also update it to `2.25.1` to benefit from the fix, as it reuses the `ComponentAttributes` class internally.

### Workarounds

Until you can upgrade, avoid rendering `{{ attributes }}` or derived objects directly if it may contain untrusted values.
Instead, use `{{ attributes.render('name') }}` for safe output of individual attributes.

### References

GitHub repository: [symfony/ux](https://github.com/symfony/ux)

## References
- https://github.com/symfony/ux/security/advisories/GHSA-5j3w-5pcr-f8hg
- https://nvd.nist.gov/vuln/detail/CVE-2025-47946
- https://github.com/symfony/ux-live-component/commit/7ad44cf56d750b9f56658ed986286a10da132ee7
- https://github.com/symfony/ux-twig-component/commit/b5d4e77db69315aeb18d2238e0e7c943d340ce76
- https://github.com/symfony/ux/commit/b5d1c85995c128cb926d47a96cfbfbd500b643a8
- https://github.com/symfony/ux/commit/c2f7738ee0969c31df7514025a7f5fc6e153932d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/ux-live-component/CVE-2025-47946.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/ux-twig-component/CVE-2025-47946.yaml
- https://github.com/symfony/ux
- https://symfony.com/blog/symfony-ux-cve-2025-47946-unsanitized-html-attribute-injection-via-componentattributes
