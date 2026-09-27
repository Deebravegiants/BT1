# [H] OpenClaw: Unbound bootstrap setup codes allow privilege escalation during pairing

## Summary
Severity: High
Advisory: GHSA-gg9v-mgcp-v6m7
CVE: CVE-2026-41386
CWE: CWE-269, CWE-648
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-gg9v-mgcp-v6m7
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Bootstrap setup codes were not bound to the intended device role and scopes, allowing first-use privilege escalation during pairing.

## Current Maintainer Triage
- Status: open
- Normalized severity: high
- Assessment: Real first-use bootstrap privilege-escalation bug fixed and shipped in v2026.3.22+, so keep open for publication with current severity.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.13-1`
- Patched versions: `>= 2026.3.22`
- First stable tag containing the fix: `v2026.3.22`

## Fix Commit(s)
- `a600c72ed7d0045a27f58bf031d2b36ecb0141c9` — 2026-03-22T23:57:15-07:00

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-gg9v-mgcp-v6m7
- https://nvd.nist.gov/vuln/detail/CVE-2026-41386
- https://github.com/openclaw/openclaw/commit/a600c72ed7d0045a27f58bf031d2b36ecb0141c9
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-unbound-bootstrap-setup-codes
