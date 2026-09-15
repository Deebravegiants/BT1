# [C] JunoClaw: MCP write tools exposed raw BIP-39 mnemonic as a tool-call parameter

## Summary
Severity: Critical
Advisory: CVE-2026-43992
Aliases: GHSA-j75q-8xvm-6c48
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-43992
Type: osv

## Details
JunoClaw is an agentic AI platform built on Juno Network. Prior to 0.x.y-security-1, every MCP write tool (send_tokens, execute_contract, instantiate_contract, upload_wasm, ibc_transfer, etc.) accepted 'mnemonic: string' as an explicit tool-call parameter. The BIP-39 seed was consequently embedded in the LLM tool-call JSON, exposing it to any transport, log, or telemetry surface in the path between the LLM provider and the MCP process. This vulnerability is fixed in 0.x.y-security-1.

## References
- https://github.com/Dragonmonk111/junoclaw/releases/tag/v0.x.y-security-1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43992.json
- https://github.com/Dragonmonk111/junoclaw/security/advisories/GHSA-j75q-8xvm-6c48
- https://nvd.nist.gov/vuln/detail/CVE-2026-43992
- https://github.com/Dragonmonk111/junoclaw/commit/339701e
