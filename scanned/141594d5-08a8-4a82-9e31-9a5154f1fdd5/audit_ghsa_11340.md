# [H] OpenClaw's MSTeams attachment redirect handling could bypass configured media host allowlists

## Summary
Severity: High
Advisory: GHSA-w76h-8m22-hpgh
CVE: CVE-2026-32037
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-w76h-8m22-hpgh
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
## Summary
In OpenClaw MSTeams media download flows, redirect handling could bypass configured `mediaAllowHosts` checks in specific attachment paths. Redirect chains were not consistently constrained to allowlisted targets before accepting fetched content.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.21-2` (latest published at triage time)
- Fixed in: `2026.2.22` (planned next release)

## Impact
Attackers able to supply or influence attachment URLs could force redirect chains to non-allowlisted targets, weakening SSRF boundary controls for MSTeams media ingestion.

## Fix Commit(s)
- `73d93dee64127a26f1acd09d0403b794cdeb4f5c`
- `b34097f62df9d1960cc22600269cd3f3284e2124`

## Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.22`). Once that npm release is published, this advisory can be published without further version-field edits.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w76h-8m22-hpgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-32037
- https://github.com/openclaw/openclaw/commit/73d93dee64127a26f1acd09d0403b794cdeb4f5c
- https://github.com/openclaw/openclaw/commit/b34097f62df9d1960cc22600269cd3f3284e2124
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-redirect-chain-bypass-of-media-host-allowlist-in-msteams-attachment-handling
