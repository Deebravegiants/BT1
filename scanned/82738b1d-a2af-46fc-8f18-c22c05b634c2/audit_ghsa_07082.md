# [H] Twig: Sandbox filter, tag and function allow-list bypass when sandbox state changes between renders for a cached `Template`

## Summary
Severity: High
Advisory: GHSA-529h-vh3j-85hq
CVE: CVE-2026-49981
CWE: CWE-693, CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-529h-vh3j-85hq
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=0 <3.27.0

## Details
### Description

The per-template filter, tag and function allow-list check is compiled into the `checkSecurity()` method of each `Template` subclass and was invoked once from the constructor, gated by `SandboxExtension::isSandboxed($source)`. `Template` instances are then cached on the `Environment` in `$loadedTemplates`, so the verdict computed at construction time was sticky for the rest of the process.

Any later change of sandbox state on the same `Environment` left that cached verdict in place: toggling `SandboxExtension::enableSandbox()`/`disableSandbox()`, swapping the policy via `setSecurityPolicy()`, a `SourcePolicyInterface` decision flip, or simply having a parent, macro or included template pre-instantiated outside the sandbox before a sandboxed render reached it. In all of these cases, the filters, tags and functions used by the affected template kept running with the original (typically empty) check, bypassing the `SecurityPolicy` allow-list.

Method, property and `__toString` allow-lists are not affected: they are enforced at every call site at runtime through `SandboxExtension::checkMethodAllowed()`, `checkPropertyAllowed()` and `ensureToStringAllowed()`, which re-read the current state on every call.

Long-lived workers (FrankenPHP, RoadRunner, Symfony Messenger consumers, FPM with hot autoloading) that share a single `Environment` between sandboxed and non-sandboxed renders are the most exposed: a single non-sandboxed render of a shared layout pre-warms its `Template` instance, after which any later sandboxed render that extends, uses, includes or imports from that layout silently skips the filter/tag/function allow-list for the pre-warmed instance.

### Resolution

The allow-list check is no longer run from the constructor. `Template` gains a public `ensureSecurityChecked()` method that calls the compiled `checkSecurity()` only when `SandboxExtension::isSandboxed($source)` returns true for the current source, and it is invoked at every entry point that can reach a `Template` instance whose security has not yet been verified against the current state: `Template::yield()`, `Template::yieldBlock()` (on the resolved block template, which covers `extends`, `use`, traits and parent blocks), `Template::getParent()` (which evaluates user code when the parent name is dynamic) and `Template::getTemplateForMacro()` (on the resolved macro template).

The explicit `checkSecurity()` calls previously emitted by `IncludeNode` and `CoreExtension::include()` are removed: the included template's own `yield()` now re-runs the check against the current sandbox state. The compiled `checkSecurity()` body is a cheap walk over compile-time-static arrays, so the per-render cost is negligible. Old cached compiled PHP files keep working unchanged: the constructor-time call they still contain is idempotent.

### Credits

Twig would like to thank Fabien Potencier for reporting and fixing the issue.

## References
- https://github.com/twigphp/Twig/security/advisories/GHSA-529h-vh3j-85hq
- https://github.com/twigphp/Twig
- https://github.com/twigphp/Twig/releases/tag/v3.27.0
