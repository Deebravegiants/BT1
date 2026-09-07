# [H] OpenClaw has Sandbox Media Root Bypass via Unnormalized `mediaUrl` / `fileUrl` Parameter Keys (CWE-22)

## Summary
Severity: High
Advisory: GHSA-hr5v-j9h9-xjhg
CVE: CVE-2026-35668
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-hr5v-j9h9-xjhg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.24

## Details
> Fixed in OpenClaw 2026.3.24, the current shipping release.

### Advisory Details
**Title**: Sandbox Media Root Bypass via Unnormalized `mediaUrl` / `fileUrl` Parameter Keys (CWE-22)

**Description**:
### Summary
A path traversal vulnerability in the agent sandbox enforcement allows a sandboxed agent to read arbitrary files from other agents' workspaces by using the `mediaUrl` or `fileUrl` parameter key in message tool calls. The `normalizeSandboxMediaParams` function only checks `["media", "path", "filePath"]` keys, while `mediaUrl` and `fileUrl` escape normalization entirely. Combined with `handlePluginAction` dropping `mediaLocalRoots` from the dispatch context, this enables a full sandbox escape where any agent can read files outside its designated sandbox root.

### Details
The vulnerability exists in two files within the messaging pipeline:

**1. Incomplete parameter key coverage in `normalizeSandboxMediaParams`:**

In `src/infra/outbound/message-action-params.ts`, the function iterates over a hardcoded allowlist of parameter keys to validate:

```typescript
// Line 212
const mediaKeys: Array<"media" | "path" | "filePath"> = ["media", "path", "filePath"];
```

The `mediaUrl` and `fileUrl` parameter keys are not included in this array. These keys are actively used by multiple channel extensions (Discord, Telegram, Slack, Matrix, Twitch) for media attachment handling, but they completely bypass the sandbox path validation performed by `resolveSandboxedMediaSource`.

**2. Dropped `mediaLocalRoots` in `handlePluginAction`:**

In `src/infra/outbound/message-action-runner.ts`, the `handlePluginAction` function dispatches actions to channel plugins but omits `mediaLocalRoots` from the context:

```typescript
// Lines 684-697
const handled = await dispatchChannelMessageAction({
    channel,
    action,
    cfg,
    params,
    accountId: accountId ?? undefined,
    requesterSenderId: input.requesterSenderId ?? undefined,
    sessionKey: input.sessionKey,
    sessionId: input.sessionId,
    agentId,
    gateway,
    toolContext: input.toolContext,
    dryRun,
    // mediaLocalRoots is MISSING here
});
```

Despite `ChannelMessageActionContext` defining `mediaLocalRoots?: readonly string[]` (in `src/channels/plugins/types.core.ts` line 478), plugins receive `undefined` and fall back to `getDefaultMediaLocalRoots()`, which permits reads of the entire `~/.openclaw/` directory tree — including all agents' workspaces.

**Attack chain:**
1. A sandboxed agent (Agent-A at `~/.openclaw/workspace/agent-a/`) calls the message tool with `{ mediaUrl: "~/.openclaw/workspace/agent-b/secret.txt" }`
2. `normalizeSandboxMediaParams` skips the `mediaUrl` key (not in allowlist)
3. `handlePluginAction` dispatches without `mediaLocalRoots`
4. Plugin calls `loadWebMedia` with default roots, which allows `~/.openclaw/workspace/**`
5. Agent-B's secret file content is read and sent as a channel attachment

### PoC

**Prerequisites:**
- Docker installed
- OpenClaw Docker image built (`openclaw-gateway:latest`)

**Steps:**

1. Start the vulnerable gateway container:

```bash
cd llm-enhance/cve-finding/Path_Traversal/CVE-2026-27522-Media_Root_Bypass-variant-exp/
docker compose up -d
sleep 5
```

2. Run the exploit:

```bash
python3 poc_exploit.py
```

3. The exploit writes a secret file to `~/.openclaw/workspace/agent-b/secret_key.txt` inside the container, then invokes `normalizeSandboxMediaParams` with Agent-A's sandbox policy and `{ mediaUrl: <agent-b-secret-path> }`. The `mediaUrl` key bypasses normalization, and `loadWebMedia` reads the file successfully.

4. Run the control experiment to confirm sandbox works for checked keys:

```bash
python3 control-sandbox_enforced.py
```

### Log of Evidence

**Exploit output:**
```
=== CVE-2026-27522 Variant: Sandbox Media Root Bypass ===

[*] Container 'openclaw-media-bypass-test' is running
[*] Running exploit script with Bun...

[VULNERABLE] mediaUrl bypassed normalizeSandboxMediaParams!
  Agent-A sandboxRoot: /root/.openclaw/workspace/agent-a
  mediaUrl targets Agent-B: /root/.openclaw/workspace/agent-b/secret_key.txt
  args after normalization: {"mediaUrl":"/root/.openclaw/workspace/agent-b/secret_key.txt"}
[EXPLOITED] Agent-B secret file content: AGENT-B-SECRET-API-KEY-sk-12345abcdef

=== EXPLOIT SUCCESSFUL ===
Agent-A read Agent-B's secret file via mediaUrl, bypassing sandbox.

[+] RESULT: VULNERABLE — mediaUrl bypasses sandbox enforcement
```

**Control experiment output:**
```
=== Control Experiment: Sandbox Enforcement for 'media' Key ===

[*] Container 'openclaw-media-bypass-test' is running
[*] Running control script with Bun...

[SAFE] normalizeSandboxMediaParams blocked 'media' key as expected!
  Error: Path escapes sandbox root (/tmp/sandbox-ZKvGQX): /tmp/victim-2cuAOO/secret.txt

=== CONTROL EXPERIMENT PASSED ===
The 'media' parameter IS correctly checked by sandbox enforcement.
Only unchecked keys (mediaUrl, fileUrl) bypass the sandbox.

[+] CONTROL PASSED: 'media' key is correctly enforced by sandbox
```

### Impact
This is a **sandbox escape** vulnerability. An attacker who can influence an agent's tool calls (via prompt injection, multi-agent interaction, or malicious plugin instruction) can read arbitrary files from other agents' workspaces. This includes:
- API keys and secrets stored in other agents' sandboxes
- Session data and conversation logs
- Configuration files with sensitive credentials
- Any file within the `~/.openclaw/` directory tree

This completely defeats the purpose of the multi-agent sandbox isolation feature, which is documented as a security boundary in the project's Docker and sandboxing documentation.

### Affected products
- **Ecosystem**: npm
- **Package name**: openclaw
- **Affected versions**: <= 2026.3.14 (current latest)
- **Patched versions**: <None>

### Severity
- **Severity**: High
- **Vector string**: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N

### Weaknesses
- **CWE**: CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')

### Occurrences

| Permalink | Description |
| :--- | :--- |
| [https://github.com/moltbot/moltbot/blob/main/src/infra/outbound/message-action-params.ts#L206-L227](https://github.com/moltbot/moltbot/blob/main/src/infra/outbound/message-action-params.ts#L206-L227) | The `normalizeSandboxMediaParams` function with incomplete `mediaKeys` allowlist — `mediaUrl` and `fileUrl` are not checked. |
| [https://github.com/moltbot/moltbot/blob/main/src/infra/outbound/message-action-runner.ts#L684-L697](https://github.com/moltbot/moltbot/blob/main/src/infra/outbound/message-action-runner.ts#L684-L697) | The `handlePluginAction` dispatch call that omits `mediaLocalRoots` from the context passed to `dispatchChannelMessageAction`. |
| [https://github.com/moltbot/moltbot/blob/main/src/channels/plugins/types.core.ts#L478](https://github.com/moltbot/moltbot/blob/main/src/channels/plugins/types.core.ts#L478) | The `ChannelMessageActionContext` type that defines `mediaLocalRoots` but never receives it from `handlePluginAction`. |

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-hr5v-j9h9-xjhg
- https://github.com/openclaw/openclaw
