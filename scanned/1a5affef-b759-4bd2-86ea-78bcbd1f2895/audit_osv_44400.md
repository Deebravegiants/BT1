# [H] Hermes Agent 0.16.0 < 0.17.0 Credential Store Overwrite via File-Write Tool

## Summary
Severity: High
Advisory: CVE-2026-82020
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82020
Type: osv

## Details
Hermes Agent 0.16.0 prior to 0.17.0 contains an improper path restriction vulnerability that allows attackers who can influence ingested message content to overwrite the credential store by bypassing sensitive-path guards that excluded the auth.json file. Attackers can craft malicious messages directing the agent's file-write tooling to overwrite the credential store without triggering any path-based protection, enabling credential tampering or unauthorized access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82020.json
- https://github.com/NousResearch/hermes-agent/releases/tag/v2026.6.19
- https://nvd.nist.gov/vuln/detail/CVE-2026-82020
- https://www.vulncheck.com/advisories/hermes-agent-credential-store-overwrite-via-file-write-tool
- https://github.com/NousResearch/hermes-agent/commit/2b67e96aec2aa2abd5e94b544cda8e564c75f9f5
- https://github.com/NousResearch/hermes-agent/commit/da28d5d113956dcf803d5cff552a120740a96a59
- https://github.com/NousResearch/hermes-agent/pull/45821
- https://github.com/NousResearch/hermes-agent
