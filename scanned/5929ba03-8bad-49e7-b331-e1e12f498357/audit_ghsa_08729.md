# [M] Twig: `template_from_string()` escapes a SourcePolicy-driven sandbox via synthesized template name

## Summary
Severity: Medium
Advisory: GHSA-24x9-r6q4-q93w
CVE: CVE-2026-46634
CWE: CWE-693
Ecosystem: Packagist
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-24x9-r6q4-q93w
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=3.9.0 <3.26.0

## Details
### Description

When the sandbox is enabled selectively via `SourcePolicyInterface` (and not globally), a sandboxed template that is allowed to call `template_from_string` and `include` can render an arbitrary inner template with no security policy enforcement.

`Environment::createTemplate()` compiles the inner string under a synthesized name (`__string_template__<hash>`), so a name/path-based `SourcePolicy` returns `false` for it, and the inner template's `checkSecurity()` becomes a no-op. From a template the integrator believes is sandboxed, an attacker can use any tag/filter/function (including `constant()` to read secrets, or `|map("system")` to execute shell commands).

### Resolution

This is a configuration trap rather than a code bug: there is no legitimate use case for exposing `template_from_string` to untrusted template authors, and propagating the parent sandbox state through `template_from_string` would require invasive changes to `SourcePolicyInterface` semantics with their own risks.

Starting with Twig 3.26.0, the documentation and the PHPDoc of `StringLoaderExtension::templateFromString()` explicitly warn against allowing `template_from_string` in a sandboxed environment (i.e. listing it in a `SecurityPolicy` allowed-functions list). Integrators using a `SourcePolicyInterface` MUST NOT allow `template_from_string` in their allowed functions; the safest option is not to register `StringLoaderExtension` at all when a sandbox is in use.

### Credits

Twig would like to thank Claude Mythos Preview (via Project Glasswing) for reporting the issue.

## References
- https://github.com/twigphp/Twig/security/advisories/GHSA-24x9-r6q4-q93w
- https://github.com/FriendsOfPHP/security-advisories/blob/master/twig/twig/CVE-2026-46634.yaml
- https://github.com/twigphp/Twig
- https://symfony.com/cve-2026-46634
