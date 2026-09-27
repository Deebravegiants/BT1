# [H] `OpenClaw: session_status` let sandboxed subagents access parent or sibling session state

## Summary
Severity: High
Advisory: GHSA-wcxr-59v9-rxr8
CVE: CVE-2026-32918
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-wcxr-59v9-rxr8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.11

## Details
### Summary

The built-in `session_status` tool did not enforce the intended session-visibility boundary. A sandboxed subagent could supply another session's `sessionKey` and inspect or modify state outside its own sandbox scope.

### Impact

This allowed a sandboxed child session to read parent or sibling session data and, in affected releases, update the target session's persisted model override.

### Affected versions

`openclaw` `<= 2026.3.8`

### Patch

Fixed in `openclaw` `2026.3.11` and included in later releases such as `2026.3.12`. Session visibility checks now enforce the sandbox boundary before reading or mutating session state.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-wcxr-59v9-rxr8
- https://nvd.nist.gov/vuln/detail/CVE-2026-32918
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.11
- https://www.vulncheck.com/advisories/openclaw-session-sandbox-escape-via-session-status-tool
