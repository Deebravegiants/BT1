# [C] OpenClaw gateway agents.files symlink escape allowed out-of-workspace file read/write

## Summary
Severity: Critical
Advisory: GHSA-fgvx-58p6-gjwc
CVE: CVE-2026-32013
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-fgvx-58p6-gjwc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
## Impact

The gateway `agents.files.get` and `agents.files.set` methods allowed symlink traversal for allowlisted workspace files. A symlinked allowlisted file (for example `AGENTS.md`) could resolve outside the agent workspace and be read/written by the gateway process.

This could enable arbitrary host file read/write within the gateway process permissions, and chained impact up to code execution depending on which files are overwritten.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.24`
- Latest published vulnerable version at patch time: `2026.2.24`
- Patched versions: `>= 2026.2.25` 

## Remediation

`agents.files` now resolves real workspace paths, enforces containment for resolved targets, rejects out-of-workspace symlink targets, and keeps in-workspace symlink targets supported. The patch also adds gateway regression tests for blocked escapes and valid in-workspace symlink behavior.

## Fix Commit(s)

- `125f4071bcbc0de32e769940d07967db47f09d3d`

## Release Process Note

`patched_versions` is intentionally pre-set to the release (`2026.2.25`). Advisory published with npm release `2026.2.25`.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-fgvx-58p6-gjwc
- https://nvd.nist.gov/vuln/detail/CVE-2026-32013
- https://github.com/openclaw/openclaw/commit/125f4071bcbc0de32e769940d07967db47f09d3d
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-symlink-traversal-in-agents-files-methods
