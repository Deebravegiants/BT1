# [M] OpenClaw's avatar symlink traversal can expose out-of-workspace local files

## Summary
Severity: Medium
Advisory: GHSA-rx3g-mvc3-qfjf
CVE: CVE-2026-32024
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-rx3g-mvc3-qfjf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
OpenClaw avatar handling allowed a symlink traversal path that could expose local files outside an agent workspace through gateway avatar surfaces.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.21`, plus prereleases `2026.2.21-1` and `2026.2.21-2`
- Latest published version at triage time (2026-02-22): `2026.2.21-2` (affected)
- Planned patched version (pre-set for release workflow): `2026.2.22`

### Details
In vulnerable builds, local avatar resolution could follow symlinks and return file bytes from outside the configured workspace boundary.

The issue was hardened in two paths:
1. Gateway avatar metadata resolution now enforces canonical containment, `O_NOFOLLOW`, and fd/file-identity checks.
2. Control UI avatar serving now rejects symlink paths and enforces fd/file-identity and size checks before reads.

### Fix Commit(s)
- `3d0337504349954237d09e4d957df5cb844d5e77`
- `6970c2c2db3ee069ef0fff0ade5cfbdd0134f9d2`

### Release Process Note
`patched_versions` is pre-set to `>= 2026.2.22` so after npm release, the remaining action is to publish this advisory.

### Impact
Confidentiality impact only: local files readable by the OpenClaw process could be disclosed via avatar response surfaces.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rx3g-mvc3-qfjf
- https://nvd.nist.gov/vuln/detail/CVE-2026-32024
- https://github.com/openclaw/openclaw/commit/3d0337504349954237d09e4d957df5cb844d5e77
- https://github.com/openclaw/openclaw/commit/6970c2c2db3ee069ef0fff0ade5cfbdd0134f9d2
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-symlink-traversal-in-avatar-handling
