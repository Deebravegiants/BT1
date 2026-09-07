# [H] OpenClaw's unsanitized session ID enables path traversal in transcript file operations

## Summary
Severity: High
Advisory: GHSA-5xfq-5mr7-426q
CVE: CVE-2026-28482
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-5xfq-5mr7-426q
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.12

## Details
## Description

OpenClaw versions **<= 2026.2.9** construct transcript file paths using an unsanitized `sessionId` and also accept `sessionFile` paths without enforcing that they stay within the agent sessions directory.

A crafted `sessionId` and/or `sessionFile` (example: `../../etc/passwd`) can cause path traversal when the gateway performs transcript file read/write operations.

**Preconditions:** an attacker must be able to authenticate to the gateway (gateway token/password). By default the gateway binds to `loopback` (local-only); configurations that expose the gateway widen the attack surface.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<= 2026.2.9`
- Fixed: `>= 2026.2.12`

## Fix

Fixed by validating session IDs (rejecting path separators / traversal sequences) and enforcing sessions-directory containment for session transcript file operations.

### Fix Commit(s)

- `4199f9889f0c307b77096a229b9e085b8d856c26`

### Additional Hardening

- `cab0abf52ac91e12ea7a0cf04fff315cf0c94d64`

## Mitigation

Upgrade to `openclaw >= 2026.2.12`.

Thanks @akhmittra for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5xfq-5mr7-426q
- https://nvd.nist.gov/vuln/detail/CVE-2026-28482
- https://github.com/openclaw/openclaw/commit/4199f9889f0c307b77096a229b9e085b8d856c26
- https://github.com/openclaw/openclaw/commit/cab0abf52ac91e12ea7a0cf04fff315cf0c94d64
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.12
- https://www.vulncheck.com/advisories/openclaw-path-traversal-via-unsanitized-sessionid-and-sessionfile-parameters
