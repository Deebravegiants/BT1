# [M] Twig: Sandbox `__toString()` policy bypass via dynamic mapping keys

## Summary
Severity: Medium
Advisory: GHSA-5v5v-ww74-355v
CVE: CVE-2026-48806
CWE: CWE-693, CWE-863
Ecosystem: Packagist
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-5v5v-ww74-355v
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=0 <3.27.0

## Details
### Description

This is a residual bypass of CVE-2026-47732 / GHSA-pr2w-4gpj-cpq4 left after the initial fix for unguarded `__toString()` calls.

In 3.26.0 the sandbox visitor was extended to wrap every child node that its parent will string-coerce at runtime with `CheckToStringNode`, gated by the new `CoercesChildrenToStringInterface`. `ArrayExpression` did not implement the interface for its mapping keys: when a dynamic key expression resolves to a `Stringable` object, `ArrayExpression::compile()` emits a raw `(string)` cast (via `StringCastUnary` for `ContextVariable` keys, and no cast at all for richer key expressions). PHP then invokes `__toString()` directly, without ever calling `SandboxExtension::ensureToStringAllowed()`.

A sandboxed template author can therefore trigger `__toString()` on any object reachable in the render context by using it as a dynamic mapping key, for example:

```twig
{% set arr = {(obj): "value"} %}
```

Direct output of the same object is correctly blocked, which makes this a clear policy enforcement gap. The reliable demonstrated impact is unauthorised disclosure of data returned by `__toString()`.

### Resolution

`ArrayExpression` now declares its dynamic mapping keys as string-coercion sites through `CoercesChildrenToStringInterface`, so the sandbox visitor wraps them with `CheckToStringNode` and the policy is consulted before PHP coerces the key to a string. The compiler also keeps an explicit `(string)` cast around the wrapped expression so PHP type errors on non-string keys are preserved.

As a side effect, any expression is now accepted as a dynamic mapping key (not only context variables); this is documented as a new feature on the 3.x branch.

### Credits

Twig would like to thank El Kharoubi Iosif for reporting the issue and Fabien Potencier for providing the fix.

## References
- https://github.com/twigphp/Twig/security/advisories/GHSA-5v5v-ww74-355v
- https://github.com/FriendsOfPHP/security-advisories/blob/master/twig/twig/CVE-2026-48806.yaml
- https://github.com/twigphp/Twig
- https://github.com/twigphp/Twig/releases/tag/v3.27.0
- https://symfony.com/blog/cve-2026-48806-sandbox-tostring-policy-bypass-via-dynamic-mapping-keys
