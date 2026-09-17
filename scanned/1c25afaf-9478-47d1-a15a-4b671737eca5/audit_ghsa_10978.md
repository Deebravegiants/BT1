# [M] OpenClaw's Conflicting Tool Identity Hints Bypass Dangerous-Tool Prompting

## Summary
Severity: Medium
Advisory: GHSA-74wf-h43j-vvmj
CVE: CVE-2026-35655
CWE: CWE-807, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-74wf-h43j-vvmj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
ACP permission resolution trusted conflicting tool identity hints from rawInput and metadata, which could suppress dangerous-tool prompting.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `e4c61723cd2d530680cc61789311d464ab8cdf60`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- src/acp/client.ts now fails closed when meta, rawInput, and title tool identities conflict instead of trusting spoofable raw input.
- src/acp/client.test.ts ships regressions for conflicting tool identity hints and dangerous-tool prompting.

OpenClaw thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-74wf-h43j-vvmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-35655
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/e4c61723cd2d530680cc61789311d464ab8cdf60
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-identity-spoofing-via-rawinput-tool-in-acp-permission-resolution
