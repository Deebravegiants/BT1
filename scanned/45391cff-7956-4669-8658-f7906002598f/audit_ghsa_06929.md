# [H] Grackle: Fail-open authorization in the MCP tool layer lets scoped agents perform cross-task and cross-session mutations (IDOR)

## Summary
Severity: High
Advisory: GHSA-f9ff-5x35-7gfw
CWE: CWE-613, CWE-639, CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-f9ff-5x35-7gfw
Type: github-advisory

## Affected
- npm: `@grackle-ai/mcp` — affected >=0
- npm: `@grackle-ai/plugin-core` — affected >=0
- npm: `@grackle-ai/auth` — affected >=0

## Details
## Summary

Authorization for scoped (agent) MCP callers is enforced **inline, per tool**, and is applied inconsistently — several mutating tools silently omit the ancestry/workspace check that their siblings perform. Because the MCP server authenticates all outbound gRPC with the full server API key and the backend gRPC handlers perform **no caller-based authorization**, the MCP tool layer is the *sole* authorization boundary. A malicious or prompt-injected scoped agent can therefore perform cross-task and cross-session operations it should not be allowed to (an IDOR / privilege-boundary bypass).

This advisory bundles the audit's **Systemic Pattern A** findings: **F2, F6, F7, F12** (and the duplicate F19).

## Affected versions

`@grackle-ai/mcp` (with `@grackle-ai/plugin-core` / `@grackle-ai/auth`) at **0.132.1** and earlier.

## Root cause

- `mcp-server.ts:111-127` (`createGrpcClients`) sets `Authorization: Bearer ${apiKey}` (the full server key) on every outbound gRPC call.
- Backend handlers (`updateTask`, `deleteTask`, `resumeTask`, `killAgent`, `getTask` in `plugin-core`) take only the request message — no `AuthContext` — and act on whatever ID is passed.
- Therefore scope must be enforced in each MCP tool handler. Some call `assertCallerIsAncestor` (`task_complete`, `task_start`, `session_attach`, `session_send_input`); their destructive siblings do not. New tools that forget the check **fail open**.

## F2 — task_update / task_delete / task_resume bypass ancestry (High)

**Location:** `packages/mcp/src/tools/task.ts:226` (task_update), `:393` (task_delete), `:465` (task_resume).

These accept an arbitrary `taskId` with only a `ROOT_TASK_ID` special-case and no `assertCallerIsAncestor`. The central dispatcher hardcodes its workspace gate to `name === "task_show"`, and these tools' Zod schemas have no `workspaceId` field (so the blanket injection is stripped). They are not in `DEFAULT_SCOPED_MCP_TOOLS` but **are** in the shipped `ORCHESTRATOR_MCP_TOOLS` / `ADMIN_MCP_TOOLS` presets.

**Exploit:** a scoped agent under the orchestrator persona learns a sibling/parent/cross-workspace task ID (via `task_list`/`task_search`), then `task_delete {taskId: <victim>}` (permanently destroys another agent's or the human parent's work) or `task_update` to flip a sibling to `complete`/`failed` or rewrite its dependency DAG and budgets.

## F6 — session_kill / session_resume bypass ancestry (Medium)

**Location:** `packages/mcp/src/tools/session.ts:95` (session_resume), `:178` (session_kill).

Call `client.killAgent` / `client.resumeAgent` directly with no auth context, unlike `session_attach`/`session_send_input`. `session_kill` is in the orchestrator preset. **Exploit:** cross-session SIGKILL DoS against a sibling agent or the root orchestrator; foreign session resume.

## F7 — Workspaceless scoped token fails open to all workspaces (Medium)

**Location:** `packages/mcp/src/mcp-server.ts:565-600`.

The per-task cross-workspace check (`task_show` block) is gated on `authContext.workspaceId` being truthy. A task created without a workspace (a supported config) mints a scoped token with `pid: ""` → `workspaceId: undefined`, so the check is skipped and the injected `workspaceId` becomes `""`, which the backend treats as "all workspaces." **Exploit:** a malicious agent in a workspaceless session calls `task_list` (no args) → reads every task in every workspace, then `task_show {taskId}` cross-workspace (title/description/branch/review-notes). `schedule_show` (in the default scoped allowlist) resolves by ID with no workspace check. Read-only cross-workspace disclosure.

## F12 — Scoped-token revocation is dead code (Low)

**Location:** `packages/auth/src/scoped-token.ts:23,142-149`.

The consuming check is wired (`auth-middleware.ts:90-92`), but `revokeTask()` is **never called outside tests** — no task-abort/stop flow invokes it — and the backing `revokedTasks` Map is in-memory only (lost on restart). A compromised agent that exfiltrated its scoped token keeps authenticating for the full 24h TTL regardless of task lifecycle.

## Remediation

- **Systemic fix:** enforce scope **centrally** in the `CallToolRequest` dispatcher (`mcp-server.ts`) via a per-tool `targetTaskIdArg` / `targetSessionIdArg` descriptor so any tool that targets a task/session **fails closed** unless the caller is an ancestor (or self).
- Immediately, add `assertCallerIsAncestor` (or self-or-ancestor) to `task_update`, `task_delete`, `task_resume`, `session_kill`, `session_resume`, mirroring `task_complete`/`task_start`.
- F7: do **not** fail open on empty `workspaceId` — treat a scoped non-root caller with no workspace as having access to *no* workspace; apply the `task_show` membership check whenever the caller is scoped and not `ROOT_TASK_ID`; add a per-id membership check to `schedule_show`.
- F12: wire `revokeTask()` into task-abort/stop flows with SQLite-backed persistence (like channel-grant revocation), or remove the dead API and document the 24h window.
- Add regression tests mirroring the existing `task_complete` ancestor tests for each mutator.

## CWEs

CWE-862 (Missing Authorization), CWE-639 (Authorization Bypass Through User-Controlled Key / IDOR), CWE-613 (Insufficient Session Expiration).

## References
- https://github.com/nick-pape/grackle/security/advisories/GHSA-f9ff-5x35-7gfw
- https://github.com/nick-pape/grackle
