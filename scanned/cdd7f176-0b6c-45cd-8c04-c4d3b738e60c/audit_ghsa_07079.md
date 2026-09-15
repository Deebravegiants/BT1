# [H] Gitea: Permanent Fork PR Workflow Approval Gate Bypass

## Summary
Severity: High
Advisory: GHSA-777r-4v59-6486
CVE: CVE-2026-58424
CWE: CWE-285, CWE-732, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:H/A:H (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-777r-4v59-6486
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.3

## Details
| Field | Value |
|-------|-------|
| **Identifier (researcher-assigned)** | GITEA-2026-004 |
| **Product** | Gitea (self-hosted Git service) |
| **Component** | Gitea Actions — fork pull request approval gate |
| **Affected versions** | All Gitea releases **`v1.20.0` and later**, including the latest `main` (`1.27.0+dev-289-gb7e95cc48c`). The buggy logic was introduced in commit `edf98a2dc3` — *"Require approval to run actions for fork pull request (#22803)"*, 2023-02-24 — and has shipped unchanged since. |
| **Fixed in** | not yet (this disclosure) |
| **Authentication required** | Yes — one unprivileged Gitea account capable of forking the target repository (the default ability for every authenticated user) |
| **User interaction required** | Exactly **once** — a repository administrator must approve a single benign fork PR's workflow run from the attacker. After that, *no further interaction is ever required* for any future fork PR from the same attacker on the same repository. |
| **Discovered by** | Prakhar Porwal — `prakharporwal2004@gmail.com` |
| **Live-verified on** | Gitea `main` at commit `b7e95cc48cc0e0d6fe24c89bb83da5b84a74490f`, 2026-05-24 |

---

## 1. Executive summary

Gitea Actions enforces an approval gate on workflow runs triggered by fork pull requests, so that an untrusted contributor cannot execute arbitrary workflow YAML on the maintainer's runner infrastructure without explicit consent. The gate is implemented by `ifNeedApproval()` in `services/actions/notifier_helper.go`. Its final clause skips the gate whenever the triggering user has **any** previously-approved run in the same repository:

```go
// services/actions/notifier_helper.go:423-433
if count, err := db.Count[actions_model.ActionRun](ctx, actions_model.FindRunOptions{
    RepoID:        repo.ID,
    TriggerUserID: user.ID,
    Approved:      true,
}); err != nil {
    return false, fmt.Errorf("CountRuns: %w", err)
} else if count > 0 {
    log.Trace("do not need approval because user %d has been approved before", user.ID)
    return false, nil
}
```

The check is scoped to `(repo_id, trigger_user_id)` only. It does not consider the pull request, the head commit, the workflow file contents, or any time window. The single approval click on a contributor's *first* fork PR is therefore interpreted by Gitea as *"this user is permanently trusted to execute any workflow YAML on this repository's CI infrastructure forever"* — for every future PR, on any branch, against any commit, regardless of what the workflow does.

This is a structural deviation from the documented intent — the in-source comment on the bypassing path reads *"if it's the first time user … triggered actions"*, implying a per-action-trigger check that the code does not actually perform. It is also a deviation from the equivalent behavior on the platform Gitea Actions is modeled after (GitHub Actions), where the first-contributor gate persists until a PR is **merged**, not merely approved-to-run.

I have live-reproduced the bypass end-to-end against a current `main` build. With **zero further interaction** from the maintainer after the one-time approval, an attacker's second PR's workflow:

- Was created with `need_approval = 0` and `approved_by = 0` in the `action_run` table (i.e. nobody ever approved it, and yet it was not gated).
- Was dispatched to the runner immediately.
- Executed arbitrary shell on the runner, with outbound network access, a populated `GITHUB_TOKEN`, and access to the cloned source.

Full receipts are in §3.

---

## 2. Affected code

### Primary

**`services/actions/notifier_helper.go:401-438`** — the `ifNeedApproval` function:

```go
func ifNeedApproval(ctx context.Context, run *actions_model.ActionRun,
                    repo *repo_model.Repository, user *user_model.User) (bool, error) {
    // 1. don't need approval if it's not a fork PR
    // 2. don't need approval if the event is `pull_request_target` since the
    //    workflow will run in the context of base branch
    if !run.IsForkPullRequest ||
       run.TriggerEvent == actions_module.GithubEventPullRequestTarget {
        return false, nil
    }

    // always need approval if the user is restricted
    if user.IsRestricted {
        return true, nil
    }

    // don't need approval if the user can write
    if perm, err := access_model.GetDoerRepoPermission(ctx, repo, user); err != nil {
        return false, fmt.Errorf("GetDoerRepoPermission: %w", err)
    } else if perm.CanWrite(unit_model.TypeActions) {
        return false, nil
    }

    // ===== VULNERABLE BLOCK ==================================================
    // don't need approval if the user has been approved before
    if count, err := db.Count[actions_model.ActionRun](ctx, actions_model.FindRunOptions{
        RepoID:        repo.ID,
        TriggerUserID: user.ID,
        Approved:      true,
    }); err != nil {
        return false, fmt.Errorf("CountRuns: %w", err)
    } else if count > 0 {
        return false, nil   // <-- permanent, unscoped bypass
    }
    // =========================================================================

    return true, nil
}
```

Called from `handleWorkflows()` (`services/actions/notifier_helper.go:339`) for every workflow run created in response to a fork PR; the return value populates the `NeedApproval` column on the `action_run` row.

### Supporting

- **`models/actions/run_list.go:84-86`** — the `FindRunOptions.Approved` filter resolves to `approved_by > 0`:
  ```go
  if opts.Approved {
      cond = cond.And(builder.Gt{"`action_run`.approved_by": 0})
  }
  ```
- **`services/actions/approve.go:25-27`** — the only writer of `ApprovedBy`, called when a repo admin clicks Approve on a run:
  ```go
  run.NeedApproval = false
  run.ApprovedBy = doer.ID
  if err := actions_model.UpdateRun(ctx, run, "need_approval", "approved_by"); err != nil {
  ```
- **`models/actions/run.go:44-45`** — schema:
  ```go
  NeedApproval bool                // may need approval if it's a fork pull request
  ApprovedBy   int64 `xorm:"index"` // who approved
  ```

There is no other writer of `ApprovedBy`, and no resetter for `NeedApproval` once a PR has been approved. The historical row is permanent and unconditional.

---

## 3. Live reproduction — receipts

The following was performed end-to-end against `main` on the date noted. Two accounts were used:

- `admin` (uid 1) — repository owner playing the maintainer
- `admin2` (uid 3) — second account playing the attacker

A fork-mode `gitea-runner v1.0.6` was registered with `ubuntu-latest:host` to enable on-host execution.

| Phase | Action | Resulting `action_run` row |
|-------|--------|---------------------------|
| 1 | `admin` creates `admin/base-repo` with `.gitea/workflows/ci.yml` (`echo hello` baseline) | — |
| 2 | `admin2` forks the repo | — |
| 3 | `admin2` opens PR #1 with a one-line README edit (no workflow change) | run #5 created, `need_approval = 1`, status = `Blocked` |
| 4 | `admin` clicks **Approve and run workflows** on PR #1 | run #5 updates: `need_approval = 0`, `approved_by = 1` (admin), status → `Success` |
| 5 | `admin2` opens PR #3 from a **brand-new branch** (`bypass-clean`) whose only change is `.gitea/workflows/ci.yml` rewritten to a malicious payload (loud `echo` + `curl` + `id` + `ls -la`) | **run #6 created, `need_approval = 0`, `approved_by = 0`** — gate skipped at creation |
| — | runner dispatches run #6 within seconds, no maintainer interaction at all | run #6 → status = `Success` |

### Final `action_run` table contents (queried directly from SQLite)

```
id  triggered_by_uid  need_approval  approved_by_uid  status_text  ref               sha
--  ----------------  -------------  ---------------  -----------  ----------------  --------
5   3                 0              1                Success      refs/pull/1/head  463c9114
6   3                 0              0                Success      refs/pull/3/head  70db2b9e
```

Row 6 is the smoking gun: `triggered_by` is `admin2` (the attacker), `approved_by` is **0** (no one ever clicked Approve), `need_approval` is **0** (the gate was never engaged in the first place), and the workflow ran to completion. The row is schema-indistinguishable from a legitimate trusted-user run.

### Actual payload log from run #6 (verbatim from `/api/v1/repos/admin/base-repo/actions/jobs/6/logs`)

```
2026-05-23T21:38:53Z local-demo-runner(version:v1.0.6) received task 2 of job test, be triggered by event: pull_request
2026-05-23T21:38:53Z workflow prepared
2026-05-23T21:38:53Z Run Main pwn
...
2026-05-23T21:38:53Z env:
2026-05-23T21:38:53Z   BASE_TOKEN: ***
2026-05-23T21:38:53Z ===== BYPASS DEMO - this workflow ran WITHOUT approval =====
2026-05-23T21:38:53Z running as: uid=501(prakharporwal) gid=20(staff) groups=20(staff),12(everyone),...
2026-05-23T21:38:53Z hostname:   PRAKHARs-MacBook-Air.local
2026-05-23T21:38:53Z uname:      Darwin PRAKHARs-MacBook-Air.local 25.5.0 Darwin Kernel Version 25.5.0...
2026-05-23T21:38:53Z GITHUB_TOKEN length = 40
2026-05-23T21:38:53Z outbound network test:
2026-05-23T21:38:53Z   HTTP 200
2026-05-23T21:38:53Z repo contents:
2026-05-23T21:38:53Z total 0
2026-05-23T21:38:53Z drwxr-xr-x  2 prakharporwal  staff   64 24 May 03:08 .
2026-05-23T21:38:53Z drwxr-xr-x  5 prakharporwal  staff  160 24 May 03:08 ..
2026-05-23T21:38:53Z ===== END DEMO =====
2026-05-23T21:38:53Z Job succeeded
```

Confirmed: arbitrary shell execution on the runner, populated `GITHUB_TOKEN` (40 chars), live outbound HTTPS (HTTP 200 to example.com), all triggered by an unapproved second fork PR.

---

## 4. Root cause analysis

The logic embodies a misreading of the unit of trust.

| Intended (per comment on line 436) | Actually implemented |
|-----------------------------------|---------------------|
| Approval is required *the first time* a user triggers actions. | Approval is required *the very first time* a user triggers actions and **never again**. |
| The unit of trust is the work being approved (the PR, or the commit). | The unit of trust is the user's identity, scoped to the repository. |

The query at line 424 does not include `PullRequestID`, `Ref`, `CommitSHA`, or any time predicate. The `action_run` row's `Ref` and `CommitSHA` fields are not consulted. Once `approved_by > 0` appears on any historical row for `(repo_id, trigger_user_id)`, the gate is monotonically skipped forever.

Concretely, the divergence is observable across these scenarios:

| Scenario | Intended | Implemented |
|----------|----------|-------------|
| Same PR, new commit on the same branch | Re-run uses existing approval (PR-scoped) | Auto-approved (user-scoped) ✓ |
| Same PR, force-push that replaces the workflow file | Re-approval requested | Auto-approved ✗ |
| Brand-new PR from same user, different workflow | Approval requested | **Auto-approved** ✗ — *the vulnerability* |
| New PR from same user months later | Approval requested | Auto-approved ✗ |
| Hundred PRs from same user in parallel | Only the first is the gate check; subsequent depend on policy | Only the very first ever needs approval ✗ |

For comparison, GitHub Actions' first-time-contributor gate persists *until a PR is merged*, not until a PR is approved-to-run; GitHub additionally supports per-PR re-approval as a separate setting. The Gitea code path does neither.

A secondary contributor is the coarse semantics of `FindRunOptions.Approved`: a single boolean (`approved_by > 0`) with no per-PR/per-commit predicate available. The fix therefore needs both a call-site change and a query-options extension.

---

## 5. Impact

| Dimension | Detail |
|-----------|--------|
| **Arbitrary code execution on the runner** | Attacker controls `run:` blocks dispatched to the project's CI compute, with whatever ambient privileges the runner has (shell, network, filesystem). Verified end-to-end above. |
| **Source code disclosure** | The runner clones the base repository read-only. A malicious workflow can exfiltrate it via any outbound channel — material confidentiality breach if the repo is private. |
| **Actions cache poisoning** | Actions cache entries are keyed and shared across branches/refs within a repo. A poisoned cache is restored into trusted (non-fork) runs that subsequently execute on the base branch — **escaping the fork sandbox transitively**, and at that point with full secret access. |
| **Artifact poisoning** | Workflow artifacts can be downloaded by other runs, including base-branch deploy workflows. |
| **Runner host compromise** | If the runner is long-lived (not ephemeral) or shares state across jobs (filesystem leftovers, mounted Docker socket, sudoers entry for the runner user), the attacker can plant persistence. |
| **Network pivoting** | Many self-hosted runners live inside corporate networks with reach to internal services that would otherwise be unreachable from the public internet. |
| **Resource abuse** | Cryptomining, denial-of-service of the CI infrastructure, bandwidth abuse. |
| **No audit signal** | The bypassed run row has `approved_by = 0` and `need_approval = false` — **schema-indistinguishable** from a legitimate trusted-user run. There is no log line, no webhook event, no UI banner stating that the approval gate was *skipped* (only that it wasn't needed). |
| **Scope** | Every repository that accepts fork pull requests **and** has Actions enabled. Public OSS projects are most exposed because anyone can open a PR. Internal corporate repos that accept fork PRs from contractors / interns / outside collaborators are equally exposed once a single such PR has been approved historically. |
| **Defense-in-depth bypass** | The approval gate is the *only* line of defense between untrusted PR YAML and CI execution on regular `pull_request` events. Remaining mitigations — per-fork-PR `GITEA_TOKEN` scoping (`models/actions/token_permissions.go:54-57`) and secret omission (`models/secret/secret.go:160-165`) — reduce blast radius but do not prevent code execution. |

---

## 6. Manual reproduction (web UI only, ~10 minutes)

This procedure uses only the Gitea web interface — no `curl`, no `git` CLI, no API tokens. It is intended for the maintainer security team to verify the vulnerability on a fresh instance.

### Prerequisites

1. A Gitea instance with **Actions enabled** (`[actions] ENABLED = true` in `app.ini`).
2. One Actions runner registered and online with the `ubuntu-latest` label (optional — see note at the end of this section).
3. Two user accounts:
   - **`maintainer`** — will own the target repository.
   - **`attacker`** — any unprivileged second account; registered through normal sign-up; no special privileges required.
4. Two browser sessions: a normal window for `maintainer`, and a private/incognito window for `attacker`. Do not flip between them in the same window.

### Phase 1 — `maintainer` creates the target repository

1. Log into Gitea as `maintainer`.
2. Top-right `+` → **New Repository**.
3. Owner = `maintainer`, Name = `gate-bypass-poc`, Visibility = Public, ☑ **Initialize Repository**, Default Branch = `main`. Click **Create Repository**.
4. On the repo home, click the **+** icon in the file tree → **New File**.
5. In the path field type:
   ```
   .gitea/workflows/ci.yml
   ```
6. Paste the following into the editor — **`name:` must be at column 0 with no leading whitespace**:
   ```yaml
   name: CI
   on: [pull_request]
   jobs:
     test:
       runs-on: [ubuntu-latest]
       steps:
         - name: hello
           run: echo "hello from gate-bypass-poc baseline"
   ```
7. Scroll down → **Commit directly to `main`** → **Commit Changes**.

### Phase 2 — `attacker` forks the repository

1. Switch to the `attacker` window. Log in.
2. Navigate to `…/maintainer/gate-bypass-poc`.
3. Click **Fork** (top-right). Accept defaults (owner = `attacker`). Click **Fork Repository**.

### Phase 3 — `attacker` opens a benign PR (PR #1)

1. On `…/attacker/gate-bypass-poc`, click `README.md` → pencil icon to edit.
2. Add any innocuous line (e.g. `Small typo fix.`).
3. Scroll down → select **Create a new branch for this commit and start a pull request** → branch name `benign-typo`. Click **Propose File Change**.
4. On the pre-filled "Open a new pull request" form, leave defaults and click **Create Pull Request**.
5. You should land on `…/maintainer/gate-bypass-poc/pulls/1`.

### Phase 4 — `maintainer` approves the first run (the one-time trust event)

1. Switch to the `maintainer` window. Open `…/maintainer/gate-bypass-poc/pulls/1`.
2. Scroll to the status checks section. You will see the yellow banner:
   > **Workflow runs from fork pull requests need approval to run** [ **Approve and run workflows** ]
3. **Before clicking**, open a second tab on `…/maintainer/gate-bypass-poc/actions`. The workflow run "Small typo fix" should be displayed with status **Blocked**. This is the gate working *correctly* for a first-time contributor.
4. Return to the PR tab. Click **Approve and run workflows**. The banner disappears; the run transitions to **Waiting** → **Running** → **Success** (or stays at Waiting if no runner is online — irrelevant for the bypass demonstration).

### Phase 5 — `attacker` opens a second PR (PR #2) with a malicious workflow change

1. Switch back to the `attacker` window.
2. On `…/attacker/gate-bypass-poc`, navigate to `.gitea/workflows/ci.yml` via the file tree. Click the pencil icon to edit.
3. **Replace the entire file** with the following (`name:` flush left, no leading whitespace anywhere):
   ```yaml
   name: CI
   on: [pull_request]
   jobs:
     test:
       runs-on: [ubuntu-latest]
       steps:
         - name: pwn
           env:
             BASE_TOKEN: ${{ github.token }}
           run: |
             echo "===== BYPASS DEMO - this workflow ran WITHOUT approval ====="
             echo "running as: $(id 2>/dev/null || echo n/a)"
             echo "hostname:   $(hostname 2>/dev/null || echo n/a)"
             echo "uname:      $(uname -a 2>/dev/null || echo n/a)"
             echo "GITHUB_TOKEN length = ${#BASE_TOKEN}"
             curl -fsS --max-time 5 https://example.com/ -o /dev/null -w "egress HTTP %{http_code}\n" || echo "(no network)"
             ls -la
             echo "===== END DEMO ====="
   ```
4. Scroll down → select **Create a new branch for this commit and start a pull request** → branch name `bypass-payload`. Click **Propose File Change**.
5. On the pre-filled PR form, click **Create Pull Request**. You should land on `…/maintainer/gate-bypass-poc/pulls/2`.

### Phase 6 — Observe the bypass

This is the critical observation.

1. As `maintainer`, open `…/maintainer/gate-bypass-poc/pulls/2`. **Scroll to the status checks section.**
   - **Expected if the gate worked:** the same yellow "Workflow runs from fork pull requests need approval to run" banner as in Phase 4.
   - **Actual:** **no banner**. The check appears straight away as pending / running / green. No approval has been requested. `maintainer` was not notified.
2. As `maintainer`, open `…/maintainer/gate-bypass-poc/actions`. The new run for "Update .gitea/workflows/ci.yml" is displayed with status **Waiting** / **Running** / **Success** — **never `Blocked`**.
3. Click into the run → `test` job → `pwn` step. You will see the payload output (`id`, hostname, uname, token length, outbound HTTPS code, file listing) — the attacker's code executed end-to-end without your consent.

### Note on the runner

If no runner is online and registered with the `ubuntu-latest` label, **the bypass is still proven** by step 1 of Phase 6 (no banner) and step 2 (status `Waiting` instead of `Blocked`). The runner only matters for visualising the payload's output. The status transition `Blocked → Waiting` for an unapproved second PR is itself the security signal — a gated run would remain `Blocked` indefinitely and the dispatcher would never look for a runner.

### Note on the YAML formatting

If you copy the workflow YAML out of this document into the Gitea web editor and inadvertently keep any leading whitespace before `name:`, Gitea will reject the file with `yaml: line 2: mapping values are not allowed in this context`. No `action_run` row is created in that case (the workflow detector silently skips unparseable files), and the bypass will *look* like it didn't fire when in fact the code path was never reached. **`name:` must sit at column 0.**

---

## 7. Verifying the bypass in the database

Open a database shell on the Gitea host. The `action_run` table contains the smoking gun.

### SQLite (default)

```bash
sqlite3 /var/lib/gitea/data/gitea.db
```

```sql
SELECT
  ar.id,
  ar.trigger_user_id,
  ar.need_approval,
  ar.approved_by,
  CASE ar.status
    WHEN 1 THEN 'Success' WHEN 2 THEN 'Failure' WHEN 3 THEN 'Cancelled'
    WHEN 4 THEN 'Skipped' WHEN 5 THEN 'Waiting' WHEN 6 THEN 'Running'
    WHEN 7 THEN 'Blocked' ELSE CAST(ar.status AS TEXT) END AS status,
  ar.ref
FROM action_run ar
JOIN repository r ON r.id = ar.repo_id
WHERE r.owner_name = 'maintainer' AND r.name = 'gate-bypass-poc'
ORDER BY ar.id;
```

Expected output after Phase 6:

```
id  trigger_user_id  need_approval  approved_by  status   ref
--  ---------------  -------------  -----------  -------  ----------------
N   <attacker uid>   0              <maint uid>  Success  refs/pull/1/head
N+1 <attacker uid>   0              0            Success  refs/pull/2/head
```

The N+1 row demonstrates the bypass: same trigger user, **never approved** (`approved_by = 0`), yet `need_approval = 0` and executed successfully. This row is schema-indistinguishable from a normal trusted-user run; an audit pipeline scanning the table cannot tell the bypass apart from a legitimate write-permission user's run.

### PostgreSQL / MySQL

The same query, against `database_name`, with `\c gitea` / `USE gitea;` first.

---


## 9. Suggested fixes

Three options, in order of preference.

### Option A (recommended) — Scope approval to the commit, not the user

Extend `FindRunOptions` with a `CommitSHA` predicate (it already exists as the field at `models/actions/run_list.go:70`) and reframe the gate check as *"has the current PR head SHA been approved by this user"*.

```diff
--- a/services/actions/notifier_helper.go
+++ b/services/actions/notifier_helper.go
@@
-    // don't need approval if the user has been approved before
-    if count, err := db.Count[actions_model.ActionRun](ctx, actions_model.FindRunOptions{
-        RepoID:        repo.ID,
-        TriggerUserID: user.ID,
-        Approved:      true,
-    }); err != nil {
-        return false, fmt.Errorf("CountRuns: %w", err)
-    } else if count > 0 {
-        return false, nil
-    }
+    // don't need approval if a prior run for this same PR-head commit was approved
+    if run.CommitSHA != "" {
+        if count, err := db.Count[actions_model.ActionRun](ctx, actions_model.FindRunOptions{
+            RepoID:        repo.ID,
+            TriggerUserID: user.ID,
+            CommitSHA:     run.CommitSHA,
+            Approved:      true,
+        }); err != nil {
+            return false, fmt.Errorf("CountRuns: %w", err)
+        } else if count > 0 {
+            return false, nil
+        }
+    }
```

This preserves the legitimate UX intent ("don't re-prompt on the same PR after a transient runner failure causes a re-run") without granting trust to future PRs or new commits on the same branch. Every new commit on the PR — including a force-push that replaces the workflow file — would re-trigger the gate, exactly as a security-sensitive deployment expects.

### Option B (stricter) — Require a merged contribution, like GitHub

Replace the "approved before" branch with "has this user had a PR merged in this repo before":

```go
if merged, err := issues_model.HasUserMergedPullRequestInRepo(ctx, repo.ID, user.ID); err != nil {
    return false, fmt.Errorf("HasUserMergedPullRequestInRepo: %w", err)
} else if merged {
    return false, nil
}
```

This matches the typical OSS-maintainer mental model: a contributor whose PR has been *merged* is trusted enough to run CI without further approval. *Approving a workflow run is not merging code*; the current logic conflates the two.

----

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-777r-4v59-6486
- https://nvd.nist.gov/vuln/detail/CVE-2026-58424
- https://github.com/go-gitea/gitea/pull/38010
- https://github.com/go-gitea/gitea/commit/699fe2ef43b9466ac1b0cb857029f91fd5b0056d
- https://github.com/go-gitea/gitea/commit/e107498f3b6fccff35455ef17430ca68df665297
- https://blog.gitea.com/release-of-1.26.3-and-1.26.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.4
