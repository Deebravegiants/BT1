# [H] OpenClaw hook transform path containment missed symlink-resolved escapes

## Summary
Severity: High
Advisory: GHSA-659f-22xc-98f2
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-659f-22xc-98f2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
## Vulnerability

Webhook transform modules were validated with lexical path checks only. A symlink under the allowed hooks transform tree could resolve outside the intended directory and be dynamically imported.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.21-2`
- Patched version (planned next release): `2026.2.22`

## Impact

When an attacker can cause a transform module path to reference a symlinked entry that resolves outside the trusted transform directory, the gateway may import and execute unintended JavaScript with gateway-process privileges.

## Attack Preconditions

- Hook transforms are enabled and reachable.
- Attacker can influence transform path resolution (for example via privileged config access and/or writable filesystem path in the transform tree).
- A symlink escape exists to attacker-controlled code.

## Remediation

- Enforce realpath-aware containment for existing path ancestors before dynamic import.
- Keep lexical containment checks for traversal and absolute-path escapes.
- Add regression coverage for:
  - transform module symlink escape rejection,
  - `hooks.transformsDir` symlink escape rejection,
  - in-root symlink allow-case.

## Fix Commit(s)

- `f4dd0577b055f77af783105bd65eae32f3d5e6a1`

OpenClaw thanks @aether-ai-agent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-659f-22xc-98f2
- https://github.com/openclaw/openclaw/commit/f4dd0577b055f77af783105bd65eae32f3d5e6a1
- https://github.com/openclaw/openclaw
