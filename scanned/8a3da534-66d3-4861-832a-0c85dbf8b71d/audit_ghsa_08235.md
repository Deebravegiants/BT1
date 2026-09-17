# [M] Twig: `{% sandbox %}{% include %}` skips checkSecurity() on cached templates (incomplete fix for CVE-2024-45411)

## Summary
Severity: Medium
Advisory: GHSA-7fxw-r6jv-74c8
CVE: CVE-2026-46638
CWE: CWE-693
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-7fxw-r6jv-74c8
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=0 <3.26.0

## Details
### Description

The fix for CVE-2024-45411 / GHSA-6j75-5wfj-gh66 added an explicit `$loaded->unwrap()->checkSecurity()` call in `CoreExtension::include()` so that a template already cached in `Environment::$loadedTemplates` is re-checked when included with `sandboxed = true`.

The deprecated but still functional `{% sandbox %}{% include ... %}{% endsandbox %}` tag path was not updated: it compiles to `enableSandbox(); yield from $this->load(...)->unwrap()->yield(...); disableSandbox();` with no `checkSecurity()` re-invocation. If the included template was loaded once outside the sandbox in the same `Environment` instance, its constructor (and therefore its compiled `checkSecurity()` call) already ran while `isSandboxed()` was `false`, so the tags/filters/functions allowlist enforced by `SecurityPolicy::checkSecurity()` is never applied.

An attacker who can author the included template gains access to every filter, function and tag registered in the environment, regardless of the sandbox policy.

### Resolution

The compiled output of `{% sandbox %}{% include %}` now calls `checkSecurity()` on the loaded template, matching the behaviour of `CoreExtension::include()` with `sandboxed = true`.

### Credits

Twig would like to thank Claude Mythos Preview (via Project Glasswing) for reporting the issue and providing the fix.

## References
- https://github.com/twigphp/Twig/security/advisories/GHSA-7fxw-r6jv-74c8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/twig/twig/CVE-2026-46638.yaml
- https://github.com/advisories/GHSA-6j75-5wfj-gh66
- https://github.com/twigphp/Twig
- https://symfony.com/cve-2026-46638
