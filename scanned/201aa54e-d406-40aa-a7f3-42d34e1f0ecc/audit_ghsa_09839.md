# [M] OpenClaw: Fake DeviceToken Bypasses Shared Auth Rate Limiting

## Summary
Severity: Medium
Advisory: GHSA-6p8r-6m93-557f
CVE: CVE-2026-41333
CWE: CWE-307, CWE-799
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-6p8r-6m93-557f
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Fake DeviceToken Bypasses Shared Auth Rate Limiting

## Current Maintainer Triage
- Status: narrow
- Normalized severity: low
- Assessment: Real in shipped mixed WS auth flow, but practical risk is mostly weak shared-password deployments since strong shared tokens remain non-bruteforceable.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `af0c0862f22ca4492406a3103d05e3628f94cbe9` — 2026-03-31T09:08:57+09:00

## Release Process Note
- The fix is already present in released version `2026.3.31`.

OpenClaw thanks @kexinoh of Tencent zhuque Lab (https://github.com/Tencent/AI-Infra-Guard)  for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-6p8r-6m93-557f
- https://github.com/openclaw/openclaw/commit/af0c0862f22ca4492406a3103d05e3628f94cbe9
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-authentication-rate-limiting-bypass-via-fake-devicetoken
