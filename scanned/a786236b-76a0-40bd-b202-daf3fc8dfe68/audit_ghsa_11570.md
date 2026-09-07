# [H] OpenClaw: Zip extraction symlink traversal could write outside destination

## Summary
Severity: High
Advisory: GHSA-jxrq-8fm4-9p58
CWE: CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-jxrq-8fm4-9p58
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
A path confinement bypass in OpenClaw ZIP extraction allowed writes outside the intended destination when a pre-existing symlink was present under the extraction root.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version at triage time: `2026.2.21-2`
- Affected versions: `<= 2026.2.21-2`
- Planned patched version for next release: `2026.2.22`

### Technical Details
The vulnerable path was in `src/infra/archive.ts` ZIP extraction logic. Output-path checks were lexical, but writes could still traverse an existing symlink in destination path segments.

The fix blocks this by:
- rejecting symlink traversal in destination path segments,
- validating resolved destination paths remain inside the extraction root,
- using no-follow file opens for ZIP output writes where supported,
- adding a regression test for pre-seeded destination symlink traversal.

### Impact
- Type: Arbitrary file write outside extraction root via symlink traversal during ZIP extraction.
- Preconditions: attacker-controlled archive extraction plus pre-existing symlink in destination path.

### Fix Commit(s)
- 4b226b74f5fd3b106a83a6347fd404172e2fd246

### Release Process Note
Patched version is pre-set to the planned next release (`2026.2.22`).
Once npm release `2026.2.22` is published, the advisory can be published without further field edits.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jxrq-8fm4-9p58
- https://github.com/openclaw/openclaw/commit/4b226b74f5fd3b106a83a6347fd404172e2fd246
- https://github.com/openclaw/openclaw
