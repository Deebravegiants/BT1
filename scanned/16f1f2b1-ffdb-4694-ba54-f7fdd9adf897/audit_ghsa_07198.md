# [C] Prompty: Server-Side Template Injection to Remote Code Execution in the @prompty/core Nunjucks Renderer

## Summary
Severity: Critical
Advisory: GHSA-w28w-gp39-m4p6
CWE: CWE-1336, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-w28w-gp39-m4p6
Type: github-advisory

## Affected
- npm: `@prompty/core` — affected >=0 <0.1.5
- npm: `@prompty/core` — affected >=2.0.0-alpha.1 <2.0.0-beta.5

## Details
## Summary
The TypeScript Nunjucks renderer evaluated untrusted `.prompty` template bodies with unrestricted JavaScript member access. An attacker-controlled template could traverse constructor and prototype properties to execute JavaScript in the host Node.js process.

## Affected packages
- npm `@prompty/core` versions `<= 0.1.4`
- npm `@prompty/core` versions `<= 2.0.0-beta.4`

## Impact
Applications that render untrusted, community-supplied, cloned, or LLM-generated `.prompty` files with the TypeScript runtime could allow attacker-controlled code execution with the privileges of the Node.js host process.

## Remediation
Upgrade to `@prompty/core` `2.0.0-beta.5` or later. The patched renderer sanitizes render inputs to own-data-only values, rejects constructor/prototype member traversal, and disallows template function calls. Ordinary interpolation, conditionals, loops, and own nested data properties remain supported.

## Fix details
The fix is merged in PR #404 and includes regression coverage for default Nunjucks rendering, explicit renderer usage, unsafe member lookups, and attempted template function calls.

## References
- https://github.com/microsoft/prompty/security/advisories/GHSA-w28w-gp39-m4p6
- https://github.com/microsoft/prompty/pull/404
- https://github.com/microsoft/prompty/commit/047756f4c8caf91c5868eeb42520c938393277b0
- https://github.com/microsoft/prompty
