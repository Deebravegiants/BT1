# [H] OpenClaw affected by potential code execution via unsafe hook module path handling in Gateway

## Summary
Severity: High
Advisory: GHSA-v6c6-vqqg-w888
CVE: CVE-2026-28456
CWE: CWE-22, CWE-427
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-v6c6-vqqg-w888
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.1.5 <2026.2.14

## Details
## Summary

OpenClaw Gateway supports hook mappings with optional JavaScript/TypeScript transform modules. In affected versions, the gateway did not sufficiently constrain configured module paths before passing them to dynamic `import()`. Under some configurations, a user who can modify gateway configuration could cause the gateway process to load and execute an unintended local module.

## Impact

Potential code execution in the OpenClaw gateway Node.js process.

This requires access that can modify gateway configuration (for example via the gateway config endpoints). Treat such access as high privilege.

## Affected Packages / Versions

- npm package: `openclaw`
- Affected: `>= 2026.1.5` and `<= 2026.2.13`

## Patched Versions

- `>= 2026.2.14`

## Fix Commit(s)

- `a0361b8ba959e8506dc79d638b6e6a00d12887e4` (restrict hook transform module loading)
- `35c0e66ed057f1a9f7ad2515fdcef516bd6584ce` (harden hooks module loading)

## Mitigation

- Upgrade to `2026.2.14` or newer.
- Avoid exposing gateway configuration endpoints to untrusted networks.
- Review config for unsafe values:
  - `hooks.mappings[].transform.module`
  - `hooks.internal.handlers[].module`

Thanks @222n5 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-v6c6-vqqg-w888
- https://nvd.nist.gov/vuln/detail/CVE-2026-28456
- https://github.com/openclaw/openclaw/commit/35c0e66ed057f1a9f7ad2515fdcef516bd6584ce
- https://github.com/openclaw/openclaw/commit/a0361b8ba959e8506dc79d638b6e6a00d12887e4
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
- https://www.vulncheck.com/advisories/openclaw-arbitrary-code-execution-via-unsafe-hook-module-path-handling
