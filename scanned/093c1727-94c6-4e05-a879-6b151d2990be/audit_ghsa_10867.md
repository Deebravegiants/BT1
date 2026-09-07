# [M] OpenClaw: Sandboxed /acp spawn requests could initialize host ACP sessions

## Summary
Severity: Medium
Advisory: GHSA-9q36-67vc-rrwg
CVE: CVE-2026-27646
CWE: CWE-284, CWE-693, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-9q36-67vc-rrwg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.7

## Details
### Summary
Sandboxed requester sessions could reach host-side ACP session initialization through `/acp spawn`.

OpenClaw already blocked `sessions_spawn({ runtime: "acp" })` from sandboxed sessions, but the slash-command path initialized ACP directly without applying the same host-runtime guard first.

### Affected Packages / Versions
- npm package: `openclaw`
- Affected versions: `<= 2026.3.2`
- Patched version: `>= 2026.3.7`

### Details
ACP sessions run on the host, not inside the OpenClaw sandbox. The direct ACP spawn path in `src/agents/acp-spawn.ts` already denied sandboxed requesters, but `/acp spawn` in `src/auto-reply/reply/commands-acp/lifecycle.ts` called `initializeSession(...)` without first applying the same restriction.

In affected versions, an already authorized sender in a sandboxed session could use `/acp spawn` to cross from sandboxed chat context into host-side ACP runtime initialization when ACP was enabled and a backend was available.

### Fix Commit(s)
- `61000b8e4ded919ca1a825d4700db4cb3fdc56e3`

### Fix Details
The fix introduced a shared ACP runtime-policy guard in `src/agents/acp-spawn.ts` and reused it from the `/acp spawn` handler in `src/auto-reply/reply/commands-acp/lifecycle.ts` before any ACP backend initialization. Regression coverage was added in `src/auto-reply/reply/commands-acp.test.ts` to prove sandboxed `/acp spawn` requests are rejected early, while existing ACP spawn behavior for non-sandboxed sessions remains unchanged.

### Release Process Note
Patched version is pre-set to `2026.3.7` so the advisory can be published once that npm release is available.

Thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9q36-67vc-rrwg
- https://nvd.nist.gov/vuln/detail/CVE-2026-27646
- https://github.com/openclaw/openclaw/commit/61000b8e4ded919ca1a825d4700db4cb3fdc56e3
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.7
- https://vulncheck.com/advisories/openclaw-mar-sandbox-escape-via-acp-spawn-command
