# [M] OpenClaw: Reject symlinks in local skill packaging script

## Summary
Severity: Medium
Advisory: GHSA-r6h2-5gqq-v5v6
CVE: CVE-2026-27485
CWE: CWE-61
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-20
Source: https://github.com/advisories/GHSA-r6h2-5gqq-v5v6
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
## Vulnerability

`skills/skill-creator/scripts/package_skill.py` (a local helper script used when authors package skills) previously followed symlinks while building `.skill` archives.

If an author runs this script on a crafted local skill directory containing symlinks to files outside the skill root, the resulting archive can include unintended file contents.

## Severity and Exposure

- **Severity: Low**
- **Execution context:** local/manual workflow only (skill author packaging step)
- **No remote trigger:** this is not reachable via normal OpenClaw gateway/chat runtime paths
- **No extraction Zip Slip in this finding:** this issue is limited to packaging-time symlink following

## Impact

- Potential unintentional disclosure of local files from the packaging machine into a generated `.skill` artifact.
- Requires local execution of the packaging script on attacker-controlled skill contents.

## Affected Components

- `skills/skill-creator/scripts/package_skill.py`

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Latest published version during triage: `2026.2.17`
- Vulnerable version range: `<= 2026.2.17`
- Planned patched version (next release): `2026.2.18`

## Remediation

- Reject symlinks during skill packaging.
- Add regression tests for symlink file and symlink directory cases.
- Update packaging guidance to document the symlink restriction.

## Fix Commit(s)

- `c275932aa4230fb7a8212fe1b9d2a18424874b3f`
- `ee1d6427b544ccadd73e02b1630ea5c29ba9a9f0`

## Related PR

- https://github.com/openclaw/openclaw/pull/20796

## Release Process Note

`patched_versions` is pre-set to the planned next release (`2026.2.18`). Once npm `openclaw@2026.2.18` is published, this advisory is ready to publish without additional edits.

Thanks @aether-ai-agent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-r6h2-5gqq-v5v6
- https://nvd.nist.gov/vuln/detail/CVE-2026-27485
- https://github.com/openclaw/openclaw/pull/20796
- https://github.com/openclaw/openclaw/commit/c275932aa4230fb7a8212fe1b9d2a18424874b3f
- https://github.com/openclaw/openclaw/commit/ee1d6427b544ccadd73e02b1630ea5c29ba9a9f0
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.19
