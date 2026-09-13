# [H] OpenClaw: Docker container escape via unvalidated bind mount config injection

## Summary
Severity: High
Advisory: GHSA-w235-x559-36mg
CVE: CVE-2026-27002
CWE: CWE-250
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-w235-x559-36mg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.15

## Details
## Summary
A configuration injection issue in the Docker tool sandbox could allow dangerous Docker options (bind mounts, host networking, unconfined profiles) to be applied, enabling container escape or host data access.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.14`
- Fixed version: `>= 2026.2.15` (next release)

## Impact
If an attacker can influence sandbox Docker configuration (or an operator pastes untrusted config), they may be able to:
- mount sensitive host paths (e.g. `/etc`, `/proc`, `/sys`, `/dev`, Docker socket)
- use `network=host` to bypass container network isolation
- use `seccompProfile=unconfined` / `apparmorProfile=unconfined` to weaken isolation

This can lead to host secret exfiltration or full host control (via Docker socket exposure).

## Fix
OpenClaw now blocks dangerous sandbox Docker settings:
- runtime enforcement when building `docker create` args
- config-schema validation for `network=host`, `seccompProfile=unconfined`, `apparmorProfile=unconfined`
- security audit findings to surface dangerous sandbox docker config

## Workarounds
- Do not configure `agents.*.sandbox.docker.binds` to mount system directories or Docker socket paths.
- Keep `agents.*.sandbox.docker.network` at `none` (default) or `bridge`.
- Do not use `unconfined` for seccomp/AppArmor profiles.

## Fix Commit(s)
- 887b209db47f1f9322fead241a1c0b043fd38339
- 1b6704ef5800152c777ea52b77aa2c8a46c13705 (docs)

## Release Process Note
This advisory is pre-populated with the planned fixed version (`>= 2026.2.15`). Once `openclaw@2026.2.15` is published to npm, publishing this advisory should be a single-click action.

Thanks @aether-ai-agent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w235-x559-36mg
- https://nvd.nist.gov/vuln/detail/CVE-2026-27002
- https://github.com/openclaw/openclaw/commit/887b209db47f1f9322fead241a1c0b043fd38339
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.15
