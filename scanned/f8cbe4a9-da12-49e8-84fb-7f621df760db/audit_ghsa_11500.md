# [M] OpenClaw: Gateway Plugin Subagent Fallback `deleteSession` Uses Synthetic `operator.admin`

## Summary
Severity: Medium
Advisory: GHSA-h4jx-hjr3-fhgc
CVE: CVE-2026-35645
CWE: CWE-266, CWE-648, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-h4jx-hjr3-fhgc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

Gateway Plugin Subagent Fallback `deleteSession` Uses Synthetic `operator.admin`

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

Gateway plugin subagent fallback `deleteSession` previously dispatched `sessions.delete` with a synthetic `operator.admin` runtime scope when no request-scoped client existed. Commit `b5d785f1a59a56c3471f2cef328f7c9a6c15f3e7` binds deletion to the caller scope instead of minting admin scope.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `b5d785f1a59a56c3471f2cef328f7c9a6c15f3e7`.

## Fix Commit(s)

- `b5d785f1a59a56c3471f2cef328f7c9a6c15f3e7`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-h4jx-hjr3-fhgc
- https://nvd.nist.gov/vuln/detail/CVE-2026-35645
- https://github.com/openclaw/openclaw/commit/b5d785f1a59a56c3471f2cef328f7c9a6c15f3e7
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-synthetic-operator-admin-in-deletesession
