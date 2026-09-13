# [H] OpenClaw bootstrap setup codes could be replayed to escalate pending pairing scopes before approval

## Summary
Severity: High
Advisory: GHSA-63f5-hhc7-cx6p
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-63f5-hhc7-cx6p
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.13

## Details
### Summary
`openclaw` versions `<= 2026.3.12` allowed bootstrap setup codes to be replayed before approval, which could widen the scopes on a pending device pairing request.

### Affected Packages / Versions
- Package: `openclaw` (`npm`)
- Affected versions: `<= 2026.3.12`
- Fixed version: `2026.3.13`

### Details
The vulnerable path was bootstrap token verification in `src/infra/device-bootstrap.ts`. In affected releases, a valid bootstrap setup code could be verified more than once before the pairing request was approved. That allowed a second verification attempt to mutate a pending device pairing and request broader scopes, including escalation from a lower operator scope to `operator.admin`, before an approver finalized the pairing.

This issue is in scope under OpenClaw's trust model because bootstrap setup codes are an authentication primitive for device pairing and the replay changed the privileges granted to the pending device.

### Fix
`openclaw@2026.3.13` makes bootstrap setup codes single-use. Current code consumes the bootstrap token record on the first successful verification, so replay attempts fail before pending scopes can be widened.

Regression coverage exists in `src/infra/device-pairing.test.ts` (`rejects bootstrap token replay before pending scope escalation can be approved`).

### Fix Commit(s)
- `1803d16d5cec970c54b0e1ac46b31b1cbade335c`

Thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-63f5-hhc7-cx6p
- https://github.com/openclaw/openclaw/commit/1803d16d5cec970c54b0e1ac46b31b1cbade335c
- https://github.com/openclaw/openclaw
