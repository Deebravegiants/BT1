# [H] Agentic-Flow: OS Command Injection in agentic-flow MCP server tools via unsanitized tool-parameter interpolation into execSync

## Summary
Severity: High
Advisory: GHSA-vcv2-r9jh-99m5
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-vcv2-r9jh-99m5
Type: github-advisory

## Affected
- npm: `agentic-flow` — affected >=0 <2.0.14

## Details
## Summary

`agentic-flow` versions `<= 2.0.13` MCP server tools interpolated attacker-influenceable tool parameters (e.g. `agent`, `task`, `name`, `language`, `agentdb` arguments) directly into shell command strings passed to `execSync()`. A malicious value reaching any of the affected MCP tools could break out of the surrounding double-quoted argument and execute arbitrary OS commands with the privileges of the user running the MCP server.

This was a partial-fix gap: prior commit `6a06854` (#158) fixed CWE-78 elsewhere in the project but missed the MCP server files entirely.

## Impact

Any MCP tool argument that the AI agent treats as data but the implementation interpolates into a shell command string becomes a command-injection vector. In MCP deployments where untrusted content (web pages, files, third-party tool output) is processed by the agent, this is reachable without direct attacker access to the host. The HTTP/SSE transports (`http-sse.ts`, `http-streaming-updated.ts`) expose the same sinks without authentication or Origin/Host validation, which may raise the effective severity in any deployment that binds them to a reachable network interface.

## Affected components

- `src/mcp/standalone-stdio.ts` — `agentic_flow_agent`, `agentic_flow_create_agent`, `agentic_flow_list_all_agents`, `agentic_flow_agent_info`, `agentic_flow_check_conflicts`, `agentic_flow_optimize_model`, `agentic_flow_list_agents`, `agent_booster_edit_file`, `agent_booster_batch_edit`, `agent_booster_parse_markdown`, `agentdb_stats`, `agentdb_pattern_store`, `agentdb_pattern_search`, `agentdb_pattern_stats`
- `src/mcp/fastmcp/servers/claude-flow-sdk.ts`
- `src/mcp/fastmcp/servers/stdio-full.ts`
- `src/mcp/fastmcp/servers/http-streaming-updated.ts`
- `src/mcp/fastmcp/servers/http-sse.ts`
- `src/mcp/fastmcp/servers/poc-stdio.ts`
- `src/mcp/fastmcp/tools/agent/{execute,list,parallel}.ts`
- `src/mcp/fastmcp/tools/swarm/orchestrate.ts`
- `src/mcp/fastmcp/tools/hooks/pretrain.ts` (depth path only)

## Proof of Concept

```ts
// Pre-fix (standalone-stdio.ts, agentic_flow_agent)
let cmd = `npx --yes agentic-flow --agent "${agent}" --task "${task}"`;
const result = execSync(cmd, { encoding: 'utf-8', ... });
```

Invoking the MCP tool with:

```json
{
  "agent": "coder",
  "task": "x\"; touch /tmp/INJECTED; id > /tmp/rce.txt; echo \""
}
```

produces, after interpolation:

```
npx --yes agentic-flow --agent "coder" --task "x"; touch /tmp/INJECTED; id > /tmp/rce.txt; echo ""
```

When `execSync` hands that to `/bin/sh -c`, the shell parses three commands: the truncated `npx`, then `touch /tmp/INJECTED`, then `id > /tmp/rce.txt; echo ""`. The marker file `/tmp/INJECTED` is created and the user's `id` output is written to `/tmp/rce.txt`.

## Patches

Fixed in [`agentic-flow@2.0.14`](https://www.npmjs.com/package/agentic-flow/v/2.0.14) — every affected call site rewritten to use `execFileSync(file, argv, { shell: false })` so attacker-controlled argv elements are passed straight to `execve(2)` without shell parsing.

Fix PR: ruvnet/agentic-flow#170 (merged at `0c2ec96`)

A regression test (`tests/security/cwe-78-mcp-execsync.test.ts`) was added that statically scans every `src/mcp/**/*.ts` file and fails the build if any new `execSync()` call is reintroduced outside of a documented exemption, plus a behavioural smoke check that the canonical PoC payload remains inert when passed as an argv element to `execFileSync`.

## Workarounds

Upgrade to `agentic-flow >= 2.0.14`. There is no in-product configuration that mitigates this without upgrading.

## Downstream pin

The `ruflo` / `claude-flow` / `@claude-flow/cli` packages bumped from `3.12.3` → `3.12.4` to pull the patched `agentic-flow`:

- `ruflo@3.12.4`
- `claude-flow@3.12.4`
- `@claude-flow/cli@3.12.4`

End users running any of `npx ruflo@latest`, `npx claude-flow@latest`, or `npx @claude-flow/cli@latest` are pinned to the fixed version.

## Credit

Reported by **hackchang** via a well-scoped red-team report package (`npm_agentic-flow_report_package_20260618_163017.zip`) that included a sink inventory, a minimized PoC payload, and a clear explanation of why this was a partial-fix gap rather than intended behaviour. The sink inventory directly drove the single-grep pass that closed every reachable call site; the PoC payload became the behavioural smoke test that proves the canonical attack stays inert as an argv element.

## References
- https://github.com/ruvnet/agentic-flow/security/advisories/GHSA-vcv2-r9jh-99m5
- https://github.com/ruvnet/agentic-flow/issues/169
- https://github.com/ruvnet/ruflo/issues/2414
- https://github.com/ruvnet/agentic-flow/pull/170
- https://github.com/ruvnet/ruflo/pull/2415
- https://github.com/ruvnet/agentic-flow
- https://github.com/ruvnet/ruflo/releases/tag/v3.12.4
- https://www.npmjs.com/package/agentic-flow/v/2.0.14
