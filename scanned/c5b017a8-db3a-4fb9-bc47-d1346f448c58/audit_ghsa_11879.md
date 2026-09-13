# [M] OpenClaw: macOS optional allowlist basename matching could bypass path-based policy

## Summary
Severity: Medium
Advisory: GHSA-7f4q-9rqh-x36p
CVE: CVE-2026-32016
CWE: CWE-426, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-7f4q-9rqh-x36p
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
On macOS node-host, optional exec-approval allowlist mode previously treated basename-only entries (for example `echo`) as trusted command matches.
This could allow a same-name local binary (for example `./echo`) to run without approval under `security=allowlist` + `ask=on-miss`.

### Scope / Preconditions
- macOS node-host path.
- Optional exec approvals feature enabled with `security=allowlist`.
- Basename-only allowlist entries configured.

Default install posture is not impacted: `security=deny` by default.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version at triage time: `2026.2.21-2`
- Vulnerable range: `<=2026.2.21-2`
- Planned patched version (next release): `>= 2026.2.22`

### Remediation
- Enforced path-only allowlist matching on macOS node-host (basename fallback removed).
- Added migration for legacy basename allowlist entries to last-resolved paths when available.
- UI/store validation now rejects non-path allowlist patterns.

### Fix Commit(s)
- dd41fadcaf58fd9deb963d6e163c56161e7b35dd

### Release Process Note
Patched version is pre-set for the planned next release (`2026.2.22`). Once that npm release is out, advisory can be published without further field edits.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7f4q-9rqh-x36p
- https://nvd.nist.gov/vuln/detail/CVE-2026-32016
- https://github.com/openclaw/openclaw/commit/dd41fadcaf58fd9deb963d6e163c56161e7b35dd
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-path-traversal-via-basename-only-allowlist-matching-on-macos
