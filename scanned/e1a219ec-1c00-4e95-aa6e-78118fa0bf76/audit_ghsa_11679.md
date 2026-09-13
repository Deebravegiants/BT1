# [M] OpenClaw: system.run allow-always persistence included shell-commented payload tails

## Summary
Severity: Medium
Advisory: GHSA-9q2p-vc84-2rwm
CWE: CWE-436, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-9q2p-vc84-2rwm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.7

## Details
OpenClaw's `system.run` allowlist analysis did not honor POSIX shell comment semantics when deriving `allow-always` persistence entries.

A caller in `security=allowlist` mode who received an `allow-always` decision could submit a shell command whose tail was commented out at runtime, for example by using an unquoted `#` before a chained payload. The runtime shell would execute only the pre-comment portion, but allowlist persistence could still analyze and store the non-executed tail as a trusted follow-up command.

Latest published npm version: `2026.3.2`

Fixed on `main` on March 7, 2026 in `939b18475d734ed75173f59507e3ebbdfe1992b7` by teaching shell tokenization and chain/pipeline analysis to stop at unquoted shell comments, so allow-always persistence now tracks only commands that the shell can actually execute. Normal real chained commands and quoted `#` literals continue to work.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.3.2`
- Patched version: `>= 2026.3.7`

## Fix Commit(s)

- `939b18475d734ed75173f59507e3ebbdfe1992b7`

## Release Process Note

npm `2026.3.7` was published on March 8, 2026. This advisory is fixed in the released package.

Thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9q2p-vc84-2rwm
- https://github.com/openclaw/openclaw/commit/939b18475d734ed75173f59507e3ebbdfe1992b7
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.7
