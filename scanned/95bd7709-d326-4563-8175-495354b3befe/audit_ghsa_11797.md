# [M] OpenClaw: Discord voice transcript owner-flag omission could expose owner-only tools in mixed-trust channels

## Summary
Severity: Medium
Advisory: GHSA-wpg9-4g4v-f9rc
CVE: CVE-2026-32035
CWE: CWE-269, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-wpg9-4g4v-f9rc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.2

## Details
### Summary
In `openclaw@2026.3.1`, the Discord voice transcript path called `agentCommand(...)` without `senderIsOwner`, and `agentCommand` defaults missing `senderIsOwner` to `true`.

This could allow a non-owner voice participant in the same channel to reach owner-only tool surfaces (`gateway`, `cron`) during voice transcript turns.

### Security model note
OpenClaw’s documented trust model is a **personal assistant** model (one trusted operator), not an adversarial multi-user boundary.

- OpenClaw does **not** treat one shared gateway/chat surface as a hardened per-user auth boundary.
- Mixed-trust deployments (mutually untrusted users sharing one gateway/channel) are outside recommended deployment boundaries.

This report is treated as a valid hardening/authorization bug because owner-only tool policy should still be applied consistently across chat-driven turns, including Discord voice transcript ingress.

### Details
Relevant path:
1. Voice transcript run omitted `senderIsOwner` in Discord voice manager.
2. Missing `senderIsOwner` defaulted to `true` in `agentCommand`.
3. Owner-only tool policy is keyed on `senderIsOwner`.
4. `gateway` and `cron` are owner-only tools.

### Impact
- Affects deployments where Discord voice is enabled and the bot is present in channels with non-owner participants.
- No gateway-auth boundary bypass was required.
- Practical risk depends strongly on whether the deployment is single-trust (recommended) or mixed-trust (not recommended).

### Severity rationale
Downgraded from high to **medium** to align with OpenClaw’s trust model and deployment assumptions:
- Requires participation in the same voice environment as the trusted operator workflow.
- Requires Discord voice path conditions (joined voice channel + transcript flow).
- Does not introduce a new cross-gateway or unauthenticated boundary bypass.

### Remediation
- Always pass explicit `senderIsOwner` from Discord voice transcript ingress.
- Fail closed (`false`) when owner status is unknown for non-local/chat ingress paths.
- Keep regression tests that verify owner/non-owner voice speaker handling.


### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.3.1`
- Patched versions: `>= 2026.3.2` (released)

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-wpg9-4g4v-f9rc
- https://nvd.nist.gov/vuln/detail/CVE-2026-32035
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-missing-owner-flag-validation-in-discord-voice-transcript-handler
