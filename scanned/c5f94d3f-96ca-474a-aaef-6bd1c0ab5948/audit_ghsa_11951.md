# [M] OpenClaw leaf subagents can bypass controlScope restrictions to send messages to child sessions

## Summary
Severity: Medium
Advisory: GHSA-x2cm-hg9c-mf5w
CVE: CVE-2026-35662
CWE: CWE-285, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-x2cm-hg9c-mf5w
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Leaf subagents could still use the send action to message controlled child sessions even when their controlScope was narrower than children.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `7679eb375294941b02214c234aff3948796969d0`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- src/auto-reply/reply/commands-subagents/action-send.ts now threads controller context through the send path.
- src/agents/subagent-control.ts now blocks send attempts unless the requester owns the target and has controlScope="children".

OpenClaw thanks @space08 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-x2cm-hg9c-mf5w
- https://nvd.nist.gov/vuln/detail/CVE-2026-35662
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/7679eb375294941b02214c234aff3948796969d0
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-missing-controlscope-enforcement-in-send-action
