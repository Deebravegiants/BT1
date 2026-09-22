# [H] OpenClaw: Command hijacking via unsafe PATH handling (bootstrapping + node-host PATH overrides)

## Summary
Severity: High
Advisory: GHSA-jqpq-mgvm-f9r6
CVE: CVE-2026-29610
CWE: CWE-427, CWE-78, CWE-807
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-jqpq-mgvm-f9r6
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
# Command hijacking via PATH handling

**Discovered:** 2026-02-04
**Reporter:** @akhmittra

## Summary

OpenClaw previously accepted untrusted PATH sources in limited situations. In affected versions, this could cause OpenClaw to resolve and execute an unintended binary ("command hijacking") when running host commands.

This issue primarily matters when OpenClaw is relying on allowlist/safe-bin protections and expects `PATH` to be trustworthy.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `< 2026.2.14`
- Patched: `>= 2026.2.14` (planned next release)

## What Is Required To Trigger This

### A) Node Host PATH override (remote command hijack)

An attacker needs all of the following:

- Authenticated/authorized access to an execution surface that can invoke node-host execution (for example, a compromised gateway or a caller that can issue `system.run`).
- A node host connected and exposing `system.run`.
- A configuration where allowlist/safe-bins are expected to restrict execution (this is not meaningful if full arbitrary exec is already allowed).
- The ability to pass request-scoped environment overrides (specifically `PATH`) into `system.run`.
- A way to place an attacker-controlled executable earlier in `PATH` (for example, a writable directory on the node host), with a name that matches an allowlisted/safe-bin command that OpenClaw will run.

Notes:

- OpenClaw deployments commonly require a gateway token/password (or equivalent transport authentication). This should not be treated as unauthenticated Internet RCE.
- This scenario typically depends on **non-standard / misconfigured deployments** (for example, granting untrusted parties access to invoke node-host execution or otherwise exposing a privileged execution surface beyond the intended trust boundary).

### B) Project-local PATH bootstrapping (local command hijack)

An attacker needs all of the following:

- The victim runs OpenClaw from within an attacker-controlled working directory (for example, cloning and running inside a malicious repository).
- That directory contains a `node_modules/.bin/openclaw` and additional attacker-controlled executables in the same directory.
- OpenClaw subsequently executes a command by name (resolved via `PATH`) that matches one of those attacker-controlled executables.

## Fix

- Project-local `node_modules/.bin` PATH bootstrapping is now **disabled by default**. If explicitly enabled, it is **append-only** (never prepended) via `OPENCLAW_ALLOW_PROJECT_LOCAL_BIN=1`.
- Node Host now ignores request-scoped `PATH` overrides.

## Fix Commit(s)

- 013e8f6b3be3333a229a066eef26a45fec47ffcc

Thanks @akhmittra for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jqpq-mgvm-f9r6
- https://nvd.nist.gov/vuln/detail/CVE-2026-29610
- https://github.com/openclaw/openclaw/commit/013e8f6b3be3333a229a066eef26a45fec47ffcc
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
- https://www.vulncheck.com/advisories/openclaw-command-hijacking-via-unsafe-path-handling
