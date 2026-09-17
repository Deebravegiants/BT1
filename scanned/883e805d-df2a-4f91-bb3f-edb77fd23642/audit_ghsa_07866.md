# [M] OpenClaw's sandbox config hash sorted primitive arrays and suppressed needed container recreation

## Summary
Severity: Medium
Advisory: GHSA-xxvh-5hwj-42pp
CVE: CVE-2026-27007
CWE: CWE-1254
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-xxvh-5hwj-42pp
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.15

## Details
## Description

`normalizeForHash` in `src/agents/sandbox/config-hash.ts` recursively sorted arrays that contained only primitive values. This made order-sensitive sandbox configuration arrays hash to the same value even when order changed.

In OpenClaw sandbox flows, this hash is used to decide whether existing sandbox containers should be recreated. As a result, order-only config changes (for example Docker `dns` and `binds` array order) could be treated as unchanged and stale containers could be reused.

This is a configuration integrity issue affecting sandbox recreation behavior.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<=2026.2.14`
- Patched (planned next release): `>=2026.2.15`
- Latest published npm version at triage time (2026-02-16): `2026.2.14`

## Remediation

Array ordering is now preserved during hash normalization; only object key ordering remains normalized for deterministic hashing.

## Fix Commit(s)

- `41ded303b4f6dae5afa854531ff837c3276ad60b`

## Release Process Note

`patched_versions` is pre-set to the planned next release (`2026.2.15`) so after npm publish, the advisory can be published directly without reopening version metadata edits.

Thanks @kexinoh ( of Tencent zhuque Lab, by https://github.com/Tencent/AI-Infra-Guard) for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xxvh-5hwj-42pp
- https://nvd.nist.gov/vuln/detail/CVE-2026-27007
- https://github.com/openclaw/openclaw/commit/41ded303b4f6dae5afa854531ff837c3276ad60b
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.15
