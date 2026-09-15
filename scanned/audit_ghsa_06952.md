# [M] Gitea: Fork-PR Actions task can read a third private repository via the collaborative-owner branch (missing fork-PR guard)

## Summary
Severity: Medium
Advisory: GHSA-fj8v-hjwv-qm88
CVE: CVE-2026-58416
CWE: CWE-280, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-fj8v-hjwv-qm88
Type: github-advisory

## Affected
- Go: `gitea.dev` — affected >=0 <1.27.0

## Details
### Summary

`GetActionsUserRepoPermission` (`models/perm/access/repo_permission.go`) decides whether an Actions
task token may access a target repo. Its cross-repo branches each enforce a fork-PR discriminator —
**except the collaborative-owner branch**, which is missing the `!task.IsForkPullRequest` guard that
its sibling has. As a result, when a private repo **B** lists owner **A** as a collaborative owner, an
**attacker-controlled fork pull-request** workflow whose base repo is owned by A is granted code-read
on B — i.e. the fork's YAML can clone a third private repository it has no rights to.

### Details

```go
// models/perm/access/repo_permission.go (v1.26.2), in GetActionsUserRepoPermission
if checkSameOwnerCrossRepoAccess(ctx, taskRepo, repo, task.IsForkPullRequest) { // passes isForkPR -> denies forks
    return maxPerm, nil
}
...
if taskRepo.IsPrivate {                                   // <-- NO IsForkPullRequest check here
    actionsUnit := repo.MustGetUnit(ctx, unit.TypeActions)
    if actionsUnit.ActionsConfig().IsCollaborativeOwner(taskRepo.OwnerID) {
        return maxPerm, nil                              // grants code-read to target repo B
    }
}
```

The sibling same-owner path correctly denies fork PRs:

```go
func checkSameOwnerCrossRepoAccess(ctx, taskRepo, targetRepo, isForkPR bool) bool {
    if isForkPR {
        return false // Fork PRs are never allowed cross-repo access to other private repositories.
    }
    ...
}
```

`taskRepo` = the repo whose workflow is running (the PR's base repo A); `repo` = the target being
cloned (B). `IsCollaborativeOwner(taskRepo.OwnerID)` asks "does target B's Actions config trust A's
owner for cross-repo read?" When B trusts ownerA, the branch returns `maxPerm` (code-read) **even when
`task.IsForkPullRequest` is true** — i.e. when the executing YAML is the fork's, not A's.

Every sibling enforces the fork-PR discriminator; except for this branch:
`checkSameOwnerCrossRepoAccess` denies forks; `ComputeTaskTokenPermissions`
(`models/actions/token_permissions.go`) only clamps the token *ceiling* to read-only for fork/cross-repo
(its own comment notes the access *decision* is in `GetActionsUserRepoPermission`, so it does not
neutralize the gap — it just makes the leak read-only); secrets (`models/secret/secret.go`) and the
approval gate (`services/actions/notifier_helper.go`) both correctly key on `IsForkPullRequest`.

**Reachability** — the runner clones target repo B over git-HTTP with the task token:
`routers/web/repo/githttp.go` → `GetDoerRepoPermission(ctx, repoB, ActionsUser)` →
`GetActionsUserRepoPermission(ctx, repoB, actionsUser, taskID)` with `IsForkPullRequest == true` →
collaborative-owner branch returns code-read → `p.CanAccess(Read, code)` passes → private clone of B
succeeds. (`CheckRepoScopedToken` in githttp is a no-op for the Actions token.)

### PoC

Setup: private base repo A (`usera/repoA`), private third repo
B (`userb/repoB`) with a planted `SECRET.txt`, B's Actions config trusting `usera` as a collaborative
owner, and a genuine running fork-PR task token (`token_hash` computed with Gitea's own `HashToken`)
presented as HTTP Basic. Requesting `GET /userb/repoB.git/info/refs?service=git-upload-pack`:

| Condition (same fork-PR token) | HTTP | Meaning |
|---|---|---|
| anonymous (no token) | 401 | auth required |
| token, A **public**, B trusts A | 404 | branch gated on `taskRepo.IsPrivate` ⇒ A public skips it |
| token, A private, B has **no** collab-owner config | 404 | no trust ⇒ denied |
| **token, A private, B trusts A (collab-owner)** | **200** | **`git clone` of private B succeeds** |
| config removed / restored | 404 / 200 | deterministic |

In the 200 case, `git clone` of private repo B succeeded and yielded its `SECRET.txt` — the full source
of a third private repo the fork-PR author has no rights to.

### Impact

Read-only confidentiality breach: discloses the full source of a *third* private repository (B) to an
untrusted external fork-PR author. Read-only, not write/RCE.

Preconditions (honest):
1. B is deliberately configured with a collaborative owner — but that is exactly the feature's intended
   use, so realistic for any deployment using it.
2. The fork PR's base repo A is itself private (the branch is gated on `taskRepo.IsPrivate`). Forking a
   private A already requires read on A, so this is a normal internal-contributor situation, not a
   weakening — the escalation is "read A (granted) → read a *different* private repo B (never granted)."
3. The fork-PR workflow must actually run — most realistically via an attacker who had one earlier PR
   approved (the "approved before" path in `ifNeedApproval`), after which fork PRs auto-run.

### Suggested remediation

Add the same fork-PR guard the sibling path has (one line):

```go
if taskRepo.IsPrivate && !task.IsForkPullRequest {
    actionsUnit := repo.MustGetUnit(ctx, unit.TypeActions)
    if actionsUnit.ActionsConfig().IsCollaborativeOwner(taskRepo.OwnerID) {
        return maxPerm, nil
    }
}
```

This flips `Vuln_ForkPR_LeaksThirdPrivateRepo` to PASS, keeps `Control_NonFork_Allowed` PASS
(legitimate collaborative-owner sharing still works), and leaves the existing
`TestGetActionsUserRepoPermission` suite all green.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-fj8v-hjwv-qm88
- https://github.com/go-gitea/gitea/pull/38214
- https://github.com/go-gitea/gitea/commit/1d43b736b5a16c5f80cfdcd9a9448a9c983ddaa0
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
