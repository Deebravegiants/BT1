# [M] OpenClaw's typed sender-key matching for toolsBySender prevents identity-collision policy bypass

## Summary
Severity: Medium
Advisory: GHSA-wpph-cjgr-7c39
CVE: CVE-2026-32039
CWE: CWE-639, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-wpph-cjgr-7c39
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
`channels.*.groups.*.toolsBySender` could match a privileged sender policy using a colliding mutable identity value (for example `senderName` or `senderUsername`) when deployments used untyped keys.

The fix introduces explicit typed sender keys (`id:`, `e164:`, `username:`, `name:`), keeps legacy untyped keys on a deprecated ID-only path, and adds regression coverage to prevent cross-identifier collisions.

### Affected Packages / Versions
- Package: npm `openclaw`
- Affected versions: `<= 2026.2.21-2`
- Latest published npm version at triage time (February 22, 2026): `2026.2.21-2`
- Patched version (planned next release): `2026.2.22`

### Impact
This is a sender-authorization bypass in group tool policy matching for deployments that use `toolsBySender` with untyped keys. Under those conditions, an attacker could inherit stronger tool permissions intended for another sender if they can force an identifier collision.

### Fix Commit(s)
- `5547a2275cb69413af3b62c795b93214fe913b57`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.22`). Once that npm release is published, this advisory should only need publishing.

OpenClaw thanks @jiseoung for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-wpph-cjgr-7c39
- https://nvd.nist.gov/vuln/detail/CVE-2026-32039
- https://github.com/openclaw/openclaw/commit/5547a2275cb69413af3b62c795b93214fe913b57
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-sender-authorization-bypass-via-identity-collision-in-toolsbysender
