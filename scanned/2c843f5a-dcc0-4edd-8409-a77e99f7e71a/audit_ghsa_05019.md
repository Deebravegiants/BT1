# [M] Twig: Sandbox `__toString()` policy bypass via `Traversable` in `join` and `replace` filters

## Summary
Severity: Medium
Advisory: GHSA-8x9c-rmqh-456c
CVE: CVE-2026-48807
CWE: CWE-693, CWE-863
Ecosystem: Packagist
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-8x9c-rmqh-456c
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=0 <3.27.0

## Details
### Description

This is a residual bypass of CVE-2026-47732 / GHSA-pr2w-4gpj-cpq4 left after the initial fix for unguarded `__toString()` calls. It covers two related coercion points that were not caught by the original patch.

**`Traversable` in `join` and `replace` filters.** `SandboxExtension::ensureToStringAllowed()` recurses into PHP arrays so that a `Stringable` object hidden inside an array argument cannot be string-coerced without consulting the security policy. The recursion stops at PHP arrays: a `Traversable` value passed at the same position is not materialised, so its contents are not policy-checked. `CoreExtension::join()` and `CoreExtension::replace()` later materialise such `Traversable` inputs through `self::toArray()` and feed them to `implode()` / `strtr()`, both of which implicitly call `__toString()` on contained `Stringable` objects. The bypass also reproduces when the container implements both `Stringable` and `Traversable`: the container's own `__toString()` is policy-checked, but the elements yielded by `getIterator()` are not, and the consuming filters still coerce them to string.

**`in` and `not in` operators.** `InBinary` and `NotInBinary` compile to `CoreExtension::inFilter()`, which falls through to PHP's `<=>` operator when comparing a string with a `Stringable` object. PHP coerces the object to string via `__toString()` without the sandbox policy being consulted. Beyond the direct side effect, `in` can also be used as a content-leak oracle: each probe against an attacker-chosen needle leaks one bit of equality, and chained probes can reconstruct the string returned by `__toString()` even when every method is denied. The bypass reproduces with both array and `Traversable` haystacks, and on both operand sides.

A sandboxed template author who is allowed to call `join` / `replace`, or to use the `in` / `not in` operators, can therefore trigger a disallowed `__toString()` method on objects reachable from the render context, even when that method is not on `SecurityPolicy::$allowedMethods`. The bypass reproduces both under global sandbox mode and when sandboxing is enabled through `SourcePolicyInterface`.

### Resolution

`SandboxExtension::ensureToStringAllowed()` now also recurses into `Traversable` operands when sandboxing is active for the current source: each value is materialised once and run through the same array-recursion path, so the policy is consulted before the filter implementation can coerce contained objects to strings. This applies to plain `Traversable` operands as well as to containers that implement both `Stringable` and `Traversable`: the container's own `__toString()` is still policy-checked, and the yielded elements are additionally checked. The materialisation is guarded by `isSandboxed($source)` so that non-sandboxed code paths do not pay the cost or change generator-exhaustion semantics.

`InBinary` and `NotInBinary` now implement `Twig\Node\CoercesChildrenToStringInterface` and declare both operands as string-coerced, so `SandboxNodeVisitor` wraps each operand in `CheckToStringNode`. The policy is consulted before `CoreExtension::inFilter()` reaches PHP's `<=>` operator, matching the existing protection on the other comparison binaries (`Equal`, `Less`, `Greater`, `Spaceship`, ...).

### Credits

Twig would like to thank Vincent55 Yang and Fabien Potencier for reporting the issues and Fabien Potencier for providing the fix.

## References
- https://github.com/twigphp/Twig/security/advisories/GHSA-8x9c-rmqh-456c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/twig/twig/CVE-2026-48807.yaml
- https://github.com/twigphp/Twig
- https://github.com/twigphp/Twig/releases/tag/v3.27.0
- https://symfony.com/blog/cve-2026-48807-sandbox-tostring-policy-bypass-via-traversable-in-join-replace-and-in-not-in-operators
