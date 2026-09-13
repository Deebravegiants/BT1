# [M] OpenClaw: Windows media loaders accepted remote-host file URLs before local path validation

## Summary
Severity: Medium
Advisory: GHSA-h3x4-hc5v-v2gm
CVE: CVE-2026-34426
CWE: CWE-40
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-h3x4-hc5v-v2gm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Windows local-media handling accepted remote-host file URLs and UNC-style paths before local-path validation, so network-hosted file targets could be treated as local content.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `4fd7feb0fd4ec16c48ed983980dba79a09b3aaf5`
- `93880717f1cd34feaa45e74e939b7a5256288901`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- src/infra/local-file-access.ts now rejects remote-host file: URLs and UNC/network paths as non-local input.
- src/media/web-media.ts, src/media-understanding/attachments.normalize.ts, and src/agents/sandbox-paths.ts all route through the shared local-file guard.

OpenClaw thanks @RacerZ-fighting, @Fushuling for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-h3x4-hc5v-v2gm
- https://nvd.nist.gov/vuln/detail/CVE-2026-34426
- https://github.com/openclaw/openclaw/pull/59182
- https://github.com/openclaw/openclaw/commit/4fd7feb0fd4ec16c48ed983980dba79a09b3aaf5
- https://github.com/openclaw/openclaw/commit/93880717f1cd34feaa45e74e939b7a5256288901
- https://github.com/openclaw/openclaw/commit/b57b680c0c34de907d57f60c38fb358e82aef8f7
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-approval-bypass-via-environment-variable-normalization
