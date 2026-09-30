# [H] OpenClaw's message tool media parameter bypasses tool policy filesystem isolation

## Summary
Severity: High
Advisory: GHSA-v8wv-jg3q-qwpq
CVE: CVE-2026-33581
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-v8wv-jg3q-qwpq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.24

## Details
## Summary

The message tool accepted `mediaUrl` and `fileUrl` aliases without applying the same sandbox localRoots validation as the canonical media path handling.

## Impact

A caller constrained to sandbox media roots could read arbitrary local files by routing them through the alias parameters.

## Affected Component

`src/infra/outbound/message-action-params.ts, src/infra/outbound/message-action-runner.ts`

## Fixed Versions

- Affected: `< 2026.3.24`
- Patched: `>= 2026.3.24`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `1d7cb6fc03` (`fix: close sandbox media root bypass for mediaUrl/fileUrl aliases`).

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-v8wv-jg3q-qwpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-33581
- https://github.com/openclaw/openclaw/commit/1d7cb6fc03552bbba00e7cffb3aa9741f5556416
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-file-read-via-mediaurl-and-fileurl-parameters
