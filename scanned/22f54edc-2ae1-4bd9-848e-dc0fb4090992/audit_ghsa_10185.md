# [M] OpenClaw: Agent gateway config mutations could change protected operator settings

## Summary
Severity: Medium
Advisory: GHSA-7jm2-g593-4qrc
CWE: CWE-1220, CWE-285
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-7jm2-g593-4qrc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.20

## Details
## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `< 2026.4.20`
- Patched version: `2026.4.20`

## Impact

The agent-facing `gateway config.patch` / `config.apply` guard did not cover several operator-trusted settings, including sandbox policy, plugin enablement, gateway auth/TLS, hook routing, MCP server configuration, SSRF policy, and filesystem hardening. A prompt-injected model with access to the owner-only gateway tool could persist changes to those settings.

This is a model-to-operator guard bypass, not a remote unauthenticated gateway compromise. Severity is medium.

## Fix

OpenClaw now blocks model-driven gateway config mutations for the broader operator-trusted path set and covers per-agent overrides and array-entry patching.

Fix commit:

- `fe30b31a97a917ecc6e92f6c85378b6b20352422`

## Release

Fixed in OpenClaw `2026.4.20`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7jm2-g593-4qrc
- https://github.com/openclaw/openclaw/commit/fe30b31a97a917ecc6e92f6c85378b6b20352422
- https://github.com/openclaw/openclaw
