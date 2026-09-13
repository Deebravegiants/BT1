# [M] openclaw-claude-bridge: sandbox is not effective - `--allowed-tools ""` does not restrict available tools

## Summary
Severity: Medium
Advisory: GHSA-7853-gqqm-vcwx
CVE: CVE-2026-39398
CWE: CWE-1188, CWE-276
Ecosystem: npm
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-7853-gqqm-vcwx
Type: github-advisory

## Affected
- npm: `openclaw-claude-bridge` — affected >=0 <2.0.0

## Details
## Affected

openclaw-claude-bridge v1.1.0

## Issue

v1.1.0 spawns the Claude Code CLI subprocess with `--allowed-tools ""` and the release notes + README claim this **"disables all CLI tools"** for sandboxing. This claim is incorrect.

Per the Claude Code CLI documentation, `--allowed-tools` (alias `--allowedTools`) is an **auto-approve allowlist** of tools that execute without permission prompts — NOT a restriction on which tools are available. The correct flag to restrict the available tool set is `--tools`:

> `--tools <tools...>`  Specify the list of available tools from the built-in set. **Use `""` to disable all tools**, `"default"` to use all tools, or specify tool names (e.g. `"Bash,Edit,Read"`).

## Impact

- All CLI tools (Read/Write/Bash/WebFetch/...) remain nominally available to the spawned subprocess.
- Actual execution behavior in `--print` non-interactive mode depends on undocumented CLI defaults (may auto-deny, may error out, may hang).
- Users who deploy the bridge behind any interface that forwards untrusted prompts (e.g., publicly exposed OpenClaw gateway, automated pipelines with web-fetched context, agents that consume tool results from other systems) may be relying on a sandbox that does not exist.

The README explicitly makes a security claim the code does not uphold, creating a false sense of safety for downstream operators. If the underlying CLI behavior changes in a future version to auto-allow tools in `--print` mode, prompt-injection attacks could trigger arbitrary Read/Write/Bash operations in the gateway's process context.

## Patches

Fixed in [v1.1.1](https://github.com/SeaL773/openclaw-claude-bridge/releases/tag/v1.1.1) (commit 8a296f5) by switching to `--tools ""`. The environment variable was also renamed from `CLAUDE_ALLOWED_TOOLS` to `CLAUDE_TOOLS` to match the flag.

## Workarounds

Setting `CLAUDE_ALLOWED_TOOLS` on v1.1.0 has no mitigating effect. Upgrade to v1.1.1 or manually edit `dist/cli-bridge.js` to replace `--allowed-tools` with `--tools`.

## References

- Fix: https://github.com/SeaL773/openclaw-claude-bridge/commit/8a296f5
- v1.1.1 notes: https://github.com/SeaL773/openclaw-claude-bridge/releases/tag/v1.1.1
- Claude Code CLI reference: https://docs.claude.com/en/docs/claude-code/cli-reference

## Credit

Found during a second-round code review.

## References
- https://github.com/SeaL773/openclaw-claude-bridge/security/advisories/GHSA-7853-gqqm-vcwx
- https://github.com/SeaL773/openclaw-claude-bridge/commit/8a296f5
- https://github.com/SeaL773/openclaw-claude-bridge
- https://github.com/SeaL773/openclaw-claude-bridge/releases/tag/v1.1.1
