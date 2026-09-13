# [M] OpenClaw: Gateway HTTP Session History Route Bypasses Operator Read Scope

## Summary
Severity: Medium
Advisory: GHSA-5jvj-hxmh-6h6j
CVE: CVE-2026-35657
CWE: CWE-639, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-5jvj-hxmh-6h6j
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.25

## Details
## Summary

Gateway HTTP Session History Route Bypasses Operator Read Scope

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

The HTTP `/sessions/:sessionKey/history` route previously authenticated bearer tokens but skipped the same `operator.read` check used by `chat.history` over WebSocket. Commit `1c45123231516fa50f8cf8522ba5ff2fb2ca7aea` makes HTTP callers declare operator scopes and rejects history reads that do not include `operator.read`.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `1c45123231516fa50f8cf8522ba5ff2fb2ca7aea`.

## Fix Commit(s)

- `1c45123231516fa50f8cf8522ba5ff2fb2ca7aea`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5jvj-hxmh-6h6j
- https://github.com/openclaw/openclaw/commit/1c45123231516fa50f8cf8522ba5ff2fb2ca7aea
- https://github.com/openclaw/openclaw
