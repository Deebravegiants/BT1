# [M] Twig: Sandbox property allowlist bypass via the `column` filter under `SourcePolicyInterface`

## Summary
Severity: Medium
Advisory: GHSA-h8vq-8gpg-mhcg
CVE: CVE-2026-48808
CWE: CWE-693, CWE-863
Ecosystem: Packagist
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-h8vq-8gpg-mhcg
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=0 <3.27.0

## Details
### Description

This is a residual bypass of CVE-2026-46635 / GHSA-vcc8-phrv-43wj that only affects sandboxing enabled through `SourcePolicyInterface` (and not the regular global sandbox mode).

`CoreExtension::column()` receives the active sandbox state via the `needs_is_sandboxed` channel as a boolean `$isSandboxed`, but then routes the per-element property reads through `SandboxExtension::checkPropertyAllowed()` without forwarding the current `Source`. `SandboxExtension::checkPropertyAllowed()` re-evaluates `isSandboxed($source)` internally; with `$source = null` the `SourcePolicyInterface`-driven decision is lost, the method short-circuits to "not sandboxed", and the property allowlist is never consulted.

A template author whose sandbox is gated by a `SourcePolicyInterface` and who has `column` on their `allowedFilters` list can therefore read any public or magic property of any object reachable in the render context, regardless of `SecurityPolicy::$allowedProperties`. Direct attribute access to the same property is blocked, and the same payload is also blocked under global sandbox mode, which makes this a clear policy enforcement gap rather than a configuration issue.

### Resolution

`CoreExtension::column()` no longer goes through the `SandboxExtension` wrapper for the property check. It calls the security policy directly: the per-source decision is already captured by the `$isSandboxed` boolean computed at the call site, so the property allowlist is enforced consistently for both global and source-policy sandboxing.

### Credits

Twig would like to thank Vincent55 Yang for reporting the issue and Fabien Potencier for providing the fix.

## References
- https://github.com/twigphp/Twig/security/advisories/GHSA-h8vq-8gpg-mhcg
- https://github.com/FriendsOfPHP/security-advisories/blob/master/twig/twig/CVE-2026-48808.yaml
- https://github.com/twigphp/Twig
- https://github.com/twigphp/Twig/releases/tag/v3.27.0
- https://symfony.com/blog/cve-2026-48808-sandbox-property-allowlist-bypass-via-the-column-filter-under-sourcepolicyinterface
