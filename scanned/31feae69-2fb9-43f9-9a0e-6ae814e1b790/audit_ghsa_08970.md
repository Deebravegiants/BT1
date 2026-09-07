# [H] Twig: Sandbox property and method bypass via object-destructuring assignment

## Summary
Severity: High
Advisory: GHSA-mm6w-gr99-p3jj
CVE: CVE-2026-46639
CWE: CWE-693
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-mm6w-gr99-p3jj
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=3.24.0 <3.26.0

## Details
### Description

The object-destructuring assignment syntax introduced in Twig 3.24.0 generates a call to `CoreExtension::getAttribute()` with the `$sandboxed` argument hardcoded to `false`, regardless of whether a `SandboxExtension` is active. This permanently disables the sandbox's property and method policy checks for every destructuring expression.

`ObjectDestructuringSetBinary::compile()` emits:

```php
CoreExtension::getAttribute($this->env, $this->source, ..., \Twig\Template::ANY_CALL, false, false, false, ...);
//                                                                                ^^^^^
//                                                                       sandbox check never runs
```

Whereas `GetAttrExpression::compile()` correctly passes `$env->hasExtension(SandboxExtension::class)`.

An attacker with write access to a sandboxed Twig template can read any public property or invoke any public getter on objects passed to the template engine, bypassing `SecurityPolicy` restrictions. The exploit requires only the `{% do %}` tag to be in `allowedTags`, which is a common configuration.

### Resolution

The destructuring compiler now forwards the active sandbox flag to `getAttribute()` so property/method allowlists are enforced.

### Credits

Twig would like to thank Anvil Secure in collaboration with Claude and Anthropic Research for reporting and fixing the issue.

## References
- https://github.com/twigphp/Twig/security/advisories/GHSA-mm6w-gr99-p3jj
- https://github.com/FriendsOfPHP/security-advisories/blob/master/twig/twig/CVE-2026-46639.yaml
- https://github.com/twigphp/Twig
- https://symfony.com/cve-2026-46639
