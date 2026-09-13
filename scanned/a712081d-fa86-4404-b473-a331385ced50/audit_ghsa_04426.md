# [H] Twig: Possible sandbox bypass when using a source policy

## Summary
Severity: High
Advisory: GHSA-2q52-x2ff-qgfr
CVE: CVE-2026-24425
CWE: CWE-693
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-2q52-x2ff-qgfr
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=2.16.0
- Packagist: `twig/twig` — affected >=3.9.0 <3.26.0

## Details
# Description

When using the sandbox with a `SourcePolicyInterface`, Twig does not always apply the sandbox restriction that forbids non-`Closure` callbacks for callback-accepting filters.

The issue affects the `sort`, `filter`, `map`, and `reduce` filters.

In the affected versions, the runtime check that rejects non-`Closure` callbacks in sandbox mode does not use the current template `Source`. As a result, when the sandbox is enabled through a source policy instead of being enabled globally, Twig can incorrectly treat the current execution as non-sandboxed for these callback checks.

This can allow user-controlled templates to pass arbitrary PHP callables to callback-accepting filters even though the template is being sandboxed through a source policy.

The issue happens when all these conditions are met:

- The sandbox is not enabled globally;
- A `SourcePolicyInterface` enables the sandbox for the rendered template;
- The template uses one of the `sort`, `filter`, `map`, or `reduce` filters;
- The callback is not a `Closure`.

# Resolution

The patch makes callback sandbox checks source-aware by propagating the current template `Source` to callback-accepting filters and using it when deciding whether sandbox restrictions apply.

# Credits

We would like to thank XavLim and Wade Sparks for reporting the issue and Fabien Potencier for fixing the issue.

## References
- https://github.com/twigphp/Twig/security/advisories/GHSA-2q52-x2ff-qgfr
- https://nvd.nist.gov/vuln/detail/CVE-2026-24425
- https://github.com/FriendsOfPHP/security-advisories/blob/master/twig/twig/CVE-2026-24425.yaml
- https://github.com/twigphp/Twig
- https://github.com/twigphp/Twig/releases/tag/v3.26.0
- https://symfony.com/cve-2026-24425
- https://www.vulncheck.com/advisories/twig-x-x-sandbox-bypass-via-sourcepolicyinterface
