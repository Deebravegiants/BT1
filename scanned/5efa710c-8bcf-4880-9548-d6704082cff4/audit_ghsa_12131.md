# [C] OpenClaw Gateway: RCE and Privilege Escalation from operator.pairing to operator.admin via device.pair.approve

## Summary
Severity: Critical
Advisory: GHSA-hf68-49fm-59cq
CVE: CVE-2026-35639
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-hf68-49fm-59cq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
device.pair.approve allowed an operator.pairing approver to approve a pending device request for broader operator scopes than the approver actually held.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `fc2d29ea926f47c428c556e92ec981441228d2a4`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- src/gateway/server-methods/devices.ts now threads caller scopes into device.pair.approve.
- src/infra/device-pairing.ts now rejects requested operator scopes that exceed the approver-held operator scope set.

OpenClaw thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-hf68-49fm-59cq
- https://nvd.nist.gov/vuln/detail/CVE-2026-35639
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/fc2d29ea926f47c428c556e92ec981441228d2a4
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-device-pair-approve-scope-validation
