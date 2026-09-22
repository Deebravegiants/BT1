# [H] ouroboros-ai: Incomplete fix of CVE-2026-47211: untrusted project .env can still reach RCE via omitted execution-routing keys

## Summary
Severity: High
Advisory: GHSA-jv2h-4p9v-wf5w
CWE: CWE-15, CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-jv2h-4p9v-wf5w
Type: github-advisory

## Affected
- PyPI: `ouroboros-ai` — affected >=0 <0.42.1

## Details
### Impact
The CVE-2026-47211 fix (0.39.0) added `_UNTRUSTED_ENV_DENYLIST` to stop an untrusted project-directory `.env` from redirecting execution. The denylist was incomplete — several execution-routing keys of the same RCE class were omitted, so a malicious cloned repo can still reach arbitrary command execution by shipping a `.env` (auto-loaded at import, no review step):

- **Backend config-home roots** `CODEX_HOME`, `OPENCODE_CONFIG`, `OPENCODE_CONFIG_DIR`, `XDG_CONFIG_HOME`: a spawned vendor CLI resolves its config from these. `CODEX_HOME=./.evil` + committed `./.evil/config.toml` redirects the nested Codex agent to attacker config — `mcp_servers.<name>.command/args` (RCE) and `approval_policy="never"` / `sandbox_mode="danger-full-access"` (silent removal of the human approval gate). (reported by matte1782)
- **MCP bridge / plugin execution roster** `OUROBOROS_MCP_CONFIG` (the YAML's server `command`/`args` are spawned via stdio_client — RCE), `OUROBOROS_PLUGIN_LOCKFILE`, `OUROBOROS_PLUGIN_TRUST_ROOT` (redirect the installed-plugin roster / trust root so `ooo <name>` dispatches into attacker code). (reported by hackkim)
- **SSRF guard toggle** `OUROBOROS_ALLOW_LOCAL_TRANSPORT` (re-enables loopback/private MCP transport targets).
- **Instruction / capability roots** `OUROBOROS_AGENTS_DIR`, `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` (replace spawned sub-agent role prompts), `OUROBOROS_RUNTIME_PROFILE` (backend selector), `OUROBOROS_TOOL_CAPABILITIES` (override YAML can lower a tool's `approval_class`, weakening the approval gate).

Additionally, the MCP bridge auto-loaded `./.ouroboros/mcp_servers.yaml` from the working directory (`create_bridge_from_env(cwd=Path.cwd())`), so running `ooo` inside a malicious repo spawned the committed roster's `command` — RCE with no `.env` at all. (cwd-branch noted by hackkim)

### Patches
Fixed in 0.42.1. All listed keys were added to `_UNTRUSTED_ENV_DENYLIST`; the cwd auto-discovery branch was removed (only the explicit `OUROBOROS_MCP_CONFIG` env var and `~/.ouroboros/mcp_servers.yaml` remain, both trusted). The regression suite now derives from the source denylist to prevent future drift.

### Workarounds
Do not run Ouroboros from an untrusted/cloned repository directory; remove any project-directory `.env` and `./.ouroboros/mcp_servers.yaml` before running.

### Credit
Reported privately via coordinated disclosure by matte1782 and hackkim (https://github.com/hackkim).

## References
- https://github.com/Q00/ouroboros/security/advisories/GHSA-jv2h-4p9v-wf5w
- https://github.com/Q00/ouroboros
