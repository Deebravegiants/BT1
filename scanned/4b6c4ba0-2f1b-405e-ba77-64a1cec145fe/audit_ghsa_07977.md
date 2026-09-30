# [H] OpenClaw exec approvals: safeBins could bypass stdin-only constraints via shell expansion

## Summary
Severity: High
Advisory: GHSA-xvhf-x56f-2hpp
CVE: CVE-2026-28463
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-xvhf-x56f-2hpp
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
## Summary

OpenClaw's exec-approvals allowlist supports a small set of "safe bins" intended to be stdin-only (no positional file arguments) when running `tools.exec.host=gateway|node` with `security=allowlist`.

In affected configurations, the allowlist validation checked pre-expansion argv tokens, but execution used a real shell (`sh -c`) which expands globs and environment variables. This allowed safe bins like `head`, `tail`, or `grep` to read arbitrary local files via tokens such as `*` or `$HOME/...` without triggering approvals.

This issue is configuration-dependent and is not exercised by default settings (default `tools.exec.host` is `sandbox`).

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<= 2026.2.13`
- Patched: `>= 2026.2.14` (planned; publish the advisory after the npm release is out)

## Impact

An authorized but untrusted caller (or prompt-injection) could cause the gateway/node process to disclose files readable by that process when host execution is enabled in allowlist mode.

## Fix

Safe-bins executions now force argv tokens to be treated as literal text at execution time (single-quoted), preventing globbing and `$VARS` expansion from turning "safe" tokens into file paths.

## Fix Commit(s)

- 77b89719d5b7e271f48b6f49e334a8b991468c3b

## Release Process Note

`patched_versions` is pre-set for the next planned release (`>= 2026.2.14`) so publishing is a single click once that npm version is available.

Thanks @christos-eth for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xvhf-x56f-2hpp
- https://nvd.nist.gov/vuln/detail/CVE-2026-28463
- https://github.com/openclaw/openclaw/commit/77b89719d5b7e271f48b6f49e334a8b991468c3b
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
- https://www.vulncheck.com/advisories/openclaw-arbitrary-file-read-via-shell-expansion-in-safe-bins-allowlist
