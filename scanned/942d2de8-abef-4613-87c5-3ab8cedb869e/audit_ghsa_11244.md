# [M] OpenClaw: Discord DM reaction ingress missed dmPolicy/allowFrom checks in restricted setups

## Summary
Severity: Medium
Advisory: GHSA-354r-7mfh-7rh2
CVE: CVE-2026-32028
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-354r-7mfh-7rh2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
### Summary
In OpenClaw `<= 2026.2.24`, Discord direct-message reaction notifications did not consistently apply the same DM authorization checks (`dmPolicy` / `allowFrom`) that are enforced for normal DM message ingress.

In restrictive DM setups, a non-allowlisted Discord user who can react to a bot-authored DM message could still enqueue a reaction-derived system event in the session.

This is a reaction-only ingress inconsistency. By itself it does not directly execute commands; practical impact depends on downstream automation/tool policy.

### Details
The DM message path already enforces `dmPolicy`/`allowFrom` authorization, but the DM reaction-notification path previously allowed event enqueue under reaction mode checks without that same authorization gate.

Fix in `main` aligns reaction ingress with normal message preflight for Discord DM/group-DM/guild policy boundaries and applies equivalent DM reaction authorization hardening for Slack to keep channel behavior consistent.

### Affected Packages / Versions
- `npm` package: `openclaw`
- Affected: `<= 2026.2.24`
- Patched: `>= 2026.2.25` 

### Fix Commit(s)
- `aedf62ac7e669a89c7b299201bf6537dc6b12e0e`

### Release Process Note
`patched_versions` is pre-set to the release (`2026.2.25`) so after npm release the advisory is published.

Thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-354r-7mfh-7rh2
- https://nvd.nist.gov/vuln/detail/CVE-2026-32028
- https://github.com/openclaw/openclaw/commit/aedf62ac7e669a89c7b299201bf6537dc6b12e0e
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-missing-authorization-check-in-discord-dm-reaction-ingress
