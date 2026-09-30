# [H] Twig: Sandbox: multiple `__toString()` policy bypasses via unguarded string coercion points

## Summary
Severity: High
Advisory: GHSA-pr2w-4gpj-cpq4
CVE: CVE-2026-47732
CWE: CWE-20
Ecosystem: Packagist
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-pr2w-4gpj-cpq4
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=0 <3.26.0

## Details
### Description

`SandboxNodeVisitor` enforces `SecurityPolicy::checkMethodAllowed()` for implicit `__toString()` calls by wrapping selected AST nodes in `CheckToStringNode`. The set of wrapped nodes is incomplete, and several Twig language constructs still trigger PHP string coercion on a `Stringable` operand without first consulting the policy. A sandboxed template author can therefore invoke `__toString()` on any object reachable in the render context, even when `__toString` on its class is not allowlisted.

Confirmed bypass vectors:

- Conditional expressions (`a ? b : c`, `a ?: b`, `a ?? b`) used as the input of a string-coercing filter or as a filter/function argument.
- The `matches` operator and the loose comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`, `<=>`), which coerce a `Stringable` operand to string and can be used as an oracle to recover the value byte by byte (no tag, filter or function needs to be allowlisted).
- Twig tests in general (which were never policy-gated), in particular `is empty` which casts a `Stringable` value via `(string) $value` in `CoreExtension::testEmpty()`.
- Null-coalesce expressions nested in concatenation, and the direct output of allowed functions or filters that return a `Stringable` object.
- Arguments passed to allowed object methods, template-name expressions of template-loading tags (`include`, `extends`, `use`, ...), dynamic attribute/property names, and spread arguments from `Traversable` objects.
- The `do` tag and the `..` range operator.

### Resolution

The sandbox now wraps every child node that the parent will string-coerce at runtime, instead of relying on a hardcoded list of node types in `SandboxNodeVisitor`. A new `Twig\Node\CoercesChildrenToStringInterface` lets nodes declare which of their children must be guarded; core nodes (concatenation, comparison and range binaries, filter/function/test expressions, `do`, `include`, `extends`, `use`, ...) implement it. Spread arguments are materialised and policy-checked via the new `SandboxExtension::ensureSpreadAllowed()`, and dynamic attribute names are checked at runtime inside `CoreExtension::getAttribute()`.

### Credits

Twig would like to thank Anthropic Glasswing and El Kharoubi Iosif for reporting the issues, and Fabien Potencier for providing the fixes.

## References
- https://github.com/twigphp/Twig/security/advisories/GHSA-pr2w-4gpj-cpq4
- https://github.com/FriendsOfPHP/security-advisories/blob/master/twig/twig/CVE-2026-47732.yaml
- https://github.com/twigphp/Twig
- https://github.com/twigphp/Twig/releases/tag/v3.26.0
- https://symfony.com/cve-2026-47732
