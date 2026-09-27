# [C] OmniRoute ACP Custom-Agent Remote Code Execution (RCE)

## Summary
Severity: Critical
Advisory: CVE-2026-88062
Aliases: GHSA-hf57-cqmx-p4gr
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88062
Type: osv

## Details
OmniRoute is an open-source AI gateway providing a single endpoint for multiple model providers. In 3.8.49 and earlier, the OmniRoute POST /api/acp/agents custom ACP agent endpoint accepted attacker-controlled binary and versionCommand values and used only a self-consistency check before execFileSync executed the selected interpreter and arguments. The same request called refreshAgentCache, and resolveVersionProbe accepted the matched command before the execFileSync sink ran it. The tokenizeVersionCommand function and DISALLOWED_VERSION_COMMAND_CHARS filter rejected a limited set of shell metacharacters but still allowed interpreter evaluation arguments. The isAuthenticated function relied on isAuthRequired, which accepted anonymous requests when requireLogin was false, while api/acp/ was absent from LOCAL_ONLY_API_PREFIXES and SPAWN_CAPABLE_PREFIXES. With requireLogin=false or during a fresh-instance bootstrap window, a remote anonymous request could supply an interpreter evaluation argument and execute arbitrary code in the server container. With requireLogin=true and a configured management password, exploitation instead required a management session or management-scoped API key. No fixed version is available as of this review.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88062.json
- https://github.com/diegosouzapw/OmniRoute/security/advisories/GHSA-hf57-cqmx-p4gr
- https://nvd.nist.gov/vuln/detail/CVE-2026-88062
- https://github.com/diegosouzapw/OmniRoute/commit/60829241fd64d0317aa6a0dd8cd7a445a5287fed
- https://github.com/diegosouzapw/OmniRoute/pull/11028
