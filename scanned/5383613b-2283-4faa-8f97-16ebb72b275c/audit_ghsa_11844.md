# [H] OpenClaw's shell env fallback trusts unvalidated SHELL path from host environment

## Summary
Severity: High
Advisory: GHSA-f8mp-vj46-cq8v
CVE: CVE-2026-32032
CWE: CWE-426, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-f8mp-vj46-cq8v
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
The shell environment fallback path could invoke an attacker-controlled shell when `SHELL` was inherited from an untrusted host environment. In affected builds, shell-env loading used `$SHELL -l -c 'env -0'` without validating that `SHELL` points to a trusted executable.

In threat-model terms, this requires local environment compromise or untrusted startup environment injection first; it is not a remote pre-auth path. The hardening patch validates `SHELL` as an absolute normalized executable, prefers `/etc/shells`, applies trusted-prefix fallback checks, and falls back safely to `/bin/sh` when validation fails. The dangerous env-var policy now also blocks `SHELL` overrides.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.21-2`
- Latest published vulnerable version: `2026.2.21-2`
- Patched versions (planned next release): `>= 2026.2.22`

## Fix Commit(s)
- `25e89cc86338ef475d26be043aa541dfdb95e52a`

## Release Process Note
The advisory pre-sets `patched_versions` to the planned next release (`2026.2.22`). After that npm release is published, maintainers can publish this advisory without further version-field edits.

OpenClaw thanks @athuljayaram for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-f8mp-vj46-cq8v
- https://nvd.nist.gov/vuln/detail/CVE-2026-32032
- https://github.com/openclaw/openclaw/commit/25e89cc86338ef475d26be043aa541dfdb95e52a
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-shell-execution-via-unvalidated-shell-environment-variable
