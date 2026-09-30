# [C] OpenClaw: Plugin subagent routes could bypass gateway authorization with synthetic admin scopes

## Summary
Severity: Critical
Advisory: GHSA-xw77-45gv-p728
CVE: CVE-2026-32916
CWE: CWE-269, CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-xw77-45gv-p728
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.3.7 <2026.3.11

## Details
## Summary
In affected versions of `openclaw`, the plugin subagent runtime dispatched gateway methods through a synthetic operator client that always carried broad administrative scopes. Plugin-owned HTTP routes using `auth: "plugin"` could therefore trigger admin-only gateway actions without normal gateway authorization.

## Impact
This is a critical authorization bypass. An external unauthenticated request to a plugin-owned route could reach privileged subagent runtime methods and perform admin-only gateway actions such as deleting sessions, reading session data, or triggering agent execution.

## Affected Packages and Versions
- Package: `openclaw` (npm)
- Affected versions: `>= 2026.3.7, < 2026.3.11`
- Fixed in: `2026.3.11`

## Technical Details
The new plugin subagent runtime preserved neither the original caller's auth context nor least-privilege scope. Instead, it executed gateway dispatches through a fabricated operator client with administrative scopes, which was reachable from plugin-owned routes that intentionally bypass normal gateway auth so plugins can perform their own webhook verification.

## Fix
OpenClaw now preserves real authorization boundaries for plugin subagent calls instead of dispatching them through synthetic admin scopes. The fix shipped in `openclaw@2026.3.11`.

## Workarounds
Upgrade to `2026.3.11` or later.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xw77-45gv-p728
- https://nvd.nist.gov/vuln/detail/CVE-2026-32916
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.11
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-in-plugin-subagent-routes-via-synthetic-admin-scopes
