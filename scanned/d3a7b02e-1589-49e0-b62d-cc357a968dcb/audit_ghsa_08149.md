# [M] OpenClaw has a Matrix allowlist bypass via displayName and cross-homeserver localpart matching

## Summary
Severity: Medium
Advisory: GHSA-rmxw-jxxx-4cpc
CVE: CVE-2026-28471
CWE: CWE-287, CWE-290
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-rmxw-jxxx-4cpc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.1.14-1 <2026.2.2

## Details
### Summary

OpenClaw Matrix DM allowlist matching could be bypassed in certain configurations.

Matrix support ships as an optional plugin (not bundled with the core install), so this only affects deployments that have installed and enabled the Matrix plugin.

### Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `>= 2026.1.14-1, < 2026.2.2`
- Patched: `>= 2026.2.2`

### Details

In affected versions, DM allowlist decisions could be made by exact-matching `channels.matrix.dm.allowFrom` entries against multiple sender-derived candidates, including:

- The sender display name (attacker-controlled and non-unique)
- The sender MXID localpart with the homeserver discarded, so `@alice:evil.example` and `@alice:trusted.example` both match `alice`

If an operator configured `channels.matrix.dm.allowFrom` with display names or bare localparts (for example, `"Alice"` or `"alice"`), a remote Matrix user may be able to impersonate an allowed identity for allowlist purposes and reach the routing/agent pipeline.

### Impact

Matrix DM allowlist identity confusion. The practical impact depends on your Matrix channel policies and what capabilities are enabled downstream.

### Mitigation

- Upgrade to `openclaw >= 2026.2.2`.
- Ensure Matrix allowlists contain only full Matrix user IDs (MXIDs) like `@user:server` (or `*`). Do not use display names or bare localparts.

### Fix Commit(s)

- `8f3bfbd1c4fb967a2ddb5b4b9a05784920814bcf`

### Release Process Note

The patched version is already published to npm; the advisory can be published once you're ready.

Thanks @MegaManSec (https://joshua.hu) of [AISLE Research Team](https://aisle.com/) for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rmxw-jxxx-4cpc
- https://nvd.nist.gov/vuln/detail/CVE-2026-28471
- https://github.com/openclaw/openclaw/commit/8f3bfbd1c4fb967a2ddb5b4b9a05784920814bcf
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.2
- https://www.vulncheck.com/advisories/openclaw-allowlist-bypass-via-displayname-and-cross-homeserver-localpart-matching-in-matrix
