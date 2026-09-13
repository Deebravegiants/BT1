# [H] Twig: Arbitrary PHP code execution via `_self.(<string>)` macro-reference compilation

## Summary
Severity: High
Advisory: GHSA-45vw-wh46-2vx8
CVE: CVE-2026-46640
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-45vw-wh46-2vx8
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=3.15.0 <3.26.0

## Details
### Description

The `obj.(expr)` dynamic-attribute syntax (added in 3.15.0 as the replacement for the deprecated `attribute()` function) lets the attribute be an arbitrary expression. When the receiver is `_self` (or any `{% import %}` alias) and the parenthesised expression is a string literal, `DotExpressionParser` short-circuits to the macro-call path and concatenates the attacker-controlled string into a `MacroReferenceExpression` name with no identifier validation. `MacroReferenceExpression::compile()` then emits that name raw into the generated PHP source.

An attacker who can supply template source can inject arbitrary PHP into the compiled template and execute it at template-load time, before `checkSecurity()` is ever called. This is a complete bypass of `SandboxExtension`, including a globally-enabled sandbox with an empty `SecurityPolicy` allowlist.

### Resolution

The parser now validates that the dynamic attribute resolves to a valid macro identifier before routing through `MacroReferenceExpression`, and the macro-reference compiler emits the name through a properly escaped path.

### Credits

Twig would like to thank Claude Mythos Preview (via Project Glasswing) for reporting the issue and providing the fix.

## References
- https://github.com/twigphp/Twig/security/advisories/GHSA-45vw-wh46-2vx8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/twig/twig/CVE-2026-46640.yaml
- https://github.com/twigphp/Twig
- https://github.com/vladko312/extras/blob/main/CVE-2026-46640.py
- https://symfony.com/cve-2026-46640
