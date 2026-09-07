# [M] OpenClaw: Node exec approvals could be replayed across nodes

## Summary
Severity: Medium
Advisory: GHSA-6x2m-hqfw-hvpj
CWE: CWE-285, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-6x2m-hqfw-hvpj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.23

## Details
## Summary
`exec.approval` requests for `host=node` were not explicitly bound to the target `nodeId`, so an approval intended for one node could be replayed for a different node under the same operator-controlled gateway fleet.

## Impact
An operator approval for a `system.run` request could be reused across nodes if the request payload did not carry node identity through approval and execution checks.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `<= 2026.2.22-2`
- Fixed: `2026.2.23` (released)

## Mitigation
Upgrade to `2026.2.23` or later once published.

## Fix Details
The fix requires and persists `nodeId` for `host=node` approval requests and rejects execution when the approving node binding does not match the invoking node.

## Fix Commit(s)
- 4a3f8438e527ac371a67fe7ac68a287f0dbe6063

## Release Process Note
`patched_versions` is pre-set to the released version (`2026.2.23`). This advisory now reflects released fix version `2026.2.23`.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-6x2m-hqfw-hvpj
- https://github.com/openclaw/openclaw/commit/4a3f8438e527ac371a67fe7ac68a287f0dbe6063
- https://github.com/openclaw/openclaw
