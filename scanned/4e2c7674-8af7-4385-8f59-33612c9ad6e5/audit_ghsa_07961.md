# [M] OpenClaw: ACP prompt-size checks missing in local stdio bridge could reduce responsiveness with very large inputs

## Summary
Severity: Medium
Advisory: GHSA-cxpw-2g23-2vgw
CVE: CVE-2026-27576
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-20
Source: https://github.com/advisories/GHSA-cxpw-2g23-2vgw
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
## Vulnerability

The ACP bridge accepted very large prompt text blocks and could assemble oversized prompt payloads before forwarding them to `chat.send`.

Because ACP runs over local stdio, this mainly affects local ACP clients (for example IDE integrations) that send unusually large inputs.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.17`
- Patched version: `2026.2.18` (planned next release)

## Impact

- Local ACP sessions may become less responsive when very large prompts are submitted
- Larger-than-expected model usage/cost when oversized text is forwarded
- No privilege escalation and no direct remote attack path in the default ACP model

## Affected Components

- `src/acp/event-mapper.ts`
- `src/acp/translator.ts`

## Remediation

- Enforce a 2 MiB prompt-text limit before concatenation
- Count inter-block newline separator bytes during pre-concatenation size checks
- Keep final outbound message-size validation before `chat.send`
- Avoid stale active-run session state when oversized prompts are rejected
- Add regression tests for oversize rejection and active-run cleanup

## Fix Commit(s)

- `732e53151e8fbdfc0501182ddb0e900878bdc1e3`
- `ebcf19746f5c500a41817e03abecadea8655654a`
- `63e39d7f57ac4ad4a5e38d17e7394ae7c4dd0b9c`

Thanks @aether-ai-agent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-cxpw-2g23-2vgw
- https://nvd.nist.gov/vuln/detail/CVE-2026-27576
- https://github.com/openclaw/openclaw/commit/63e39d7f57ac4ad4a5e38d17e7394ae7c4dd0b9c
- https://github.com/openclaw/openclaw/commit/8ae2d5110f6ceadef73822aa3db194fb60d2ba68
- https://github.com/openclaw/openclaw/commit/ebcf19746f5c500a41817e03abecadea8655654a
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.19
