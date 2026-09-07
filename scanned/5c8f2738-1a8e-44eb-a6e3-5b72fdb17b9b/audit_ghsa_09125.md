# [C] Twig: PHP code injection via `{% use %}` template name

## Summary
Severity: Critical
Advisory: GHSA-7p85-w9px-jpjp
CVE: CVE-2026-46633
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-7p85-w9px-jpjp
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=0 <3.26.0

## Details
### Description

`Compiler::string()` escapes `"`, `$`, `\`, NUL and TAB when generating PHP double-quoted string literals, but does not escape single quotes. In `ModuleNode::compileConstructor()`, the template name from a `{% use %}` tag is compiled via `subcompile()` -> `string()` and placed inside a surrounding PHP single-quoted string literal. A template name containing a single quote terminates that surrounding string early, allowing arbitrary PHP expressions to be injected into the compiled cache file.

The injected code executes within the PHP process when the cache file is first loaded, bypassing the Twig sandbox entirely and achieving remote code execution. `SecurityPolicy` unconditionally allows `{% use %}` regardless of the configured `allowedTags`, so this primitive is reachable from sandboxed templates as well.

### Resolution

`Compiler::string()` now also escapes single quotes so that template names placed inside single-quoted PHP literals can no longer break out of the surrounding context.

### Credits

Twig would like to thank Anvil Secure in collaboration with Claude and Anthropic Research for reporting the issue and providing the fix.

## References
- https://github.com/twigphp/Twig/security/advisories/GHSA-7p85-w9px-jpjp
- https://github.com/FriendsOfPHP/security-advisories/blob/master/twig/twig/CVE-2026-46633.yaml
- https://github.com/twigphp/Twig
- https://symfony.com/cve-2026-46633
