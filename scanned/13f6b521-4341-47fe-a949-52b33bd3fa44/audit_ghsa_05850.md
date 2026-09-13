# [H] Vikunja has cross-tenant IDOR in kanban move-task endpoint via unauthorized body task_id

## Summary
Severity: High
Advisory: GHSA-5pg6-m483-7vrg
CVE: CVE-2026-55066
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-5pg6-m483-7vrg
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.4.0

## Details
## Summary

The kanban endpoint `POST /api/v1/projects/{project}/views/{view}/buckets/{bucket}/tasks`
moves a task into a bucket. The task is identified by `task_id` in the **request
body**. The endpoint's authorization check (`TaskBucket.CanUpdate`) only verifies
that the caller may update the *project/view/bucket named in the URL* — it never
checks any permission on `task_id`.

Any authenticated user can therefore supply another user's task ID (task IDs are
a global, sequential integer space) against a kanban bucket in their **own**
project. The server loads that victim task with no authorization check, returns
its full contents in the response, and — when the target bucket is a "done"
bucket — writes to the victim task's row.

This is the same vulnerability class Vikunja has already remediated for task
relations (CVE-2026-33676), task attachments (CVE-2026-33678), task comments
(CVE-2026-33313) and CalDAV task read (CVE-2026-35598). `TaskBucket` is the
task-child operation that was missed.

---

## Root cause

### 1. `task_id` is body-controlled and never permission-checked

`pkg/models/kanban_task_bucket.go:32`:

    type TaskBucket struct {
        BucketID      int64 `... json:"bucket_id" param:"bucket"`
        TaskID        int64 `... json:"task_id"`              // body-bound only — no param tag
        ProjectViewID int64 `... json:"project_view_id" param:"view"`
        ProjectID     int64 `xorm:"-" json:"-" param:"project"`
        ...
    }

The web handler `UpdateWeb` (`pkg/web/handler/update.go`) populates the struct via
`ctx.Bind`, which binds both URL path params (`param:` tags) **and** the JSON body.
`BucketID`, `ProjectViewID`, `ProjectID` come from the trusted URL; `TaskID` comes
entirely from the attacker-controlled body.

### 2. `CanUpdate` authorizes the URL, not the task

`pkg/models/kanban_task_bucket.go:52`:

    func (b *TaskBucket) CanUpdate(s *xorm.Session, a web.Auth) (bool, error) {
        bucket := Bucket{ID: b.BucketID, ProjectID: b.ProjectID, ProjectViewID: b.ProjectViewID}
        return bucket.canDoBucket(s, a)
    }

`canDoBucket` (`pkg/models/kanban_permissions.go:46`) resolves the bucket/view and
ends in `Project{ID: pv.ProjectID}.CanUpdate(s, a)` — a permission check on the
**project from the URL**. `b.TaskID` is never referenced. The attacker owns that
project, so the check passes.

### 3. The task is loaded and mutated with no authorization

`updateTaskBucket` (`pkg/models/kanban_task_bucket.go:119`):

    task := &Task{ID: b.TaskID}
    err = task.ReadOne(s, a)            // loads ANY task by ID — no permission check

`Task.ReadOne` (`pkg/models/tasks.go:1967`) calls `GetTaskByIDSimple` +
`addMoreInfoToTasks`; it performs no authorization (authorization normally lives
in the separate `Task.CanRead`, which this internal call path bypasses).

- **Read:** the fully populated victim task is assigned to `b.Task` (line 227) and
  returned by the `Update` handler in the response `"task"` field.
- **Write:** if the target bucket is the view's done bucket
  (`view.DoneBucketID == b.BucketID && !task.Done`, line 141), the handler sets
  `task.Done = true` and persists it to the victim's task row:

      _, err = s.Where("id = ?", task.ID).
          Cols("done", "due_date", "start_date", "end_date", "done_at").
          Update(task)

---

## Proof of Concept

The attacker is any normal authenticated user. They first create their own kanban
project/view/bucket (free for every user), then:

    POST /api/v1/projects/{ATTACKER_PROJECT}/views/{ATTACKER_VIEW}/buckets/{ATTACKER_BUCKET}/tasks HTTP/1.1
    Host: TARGET
    Authorization: Bearer {ATTACKER_JWT}
    Content-Type: application/json

    {"task_id": {VICTIM_TASK_ID}}

The `200` response body contains the victim task in full under `"task"` — title,
description, dates, assignees, labels, attachment list, reactions. Task IDs are a
global sequential counter, so iterating `task_id` enumerates every task on the
instance.

If `ATTACKER_BUCKET` is the done bucket of `ATTACKER_VIEW`, the same request also
flips the victim task to done (`done = true`, `done_at` set).

---

## Impact

Any authenticated low-privilege user can:

- **Read any task on the instance** by sequential ID, across every other user,
  project and organization — a full cross-tenant information disclosure of task
  titles, descriptions, assignees, labels and attachment metadata.
- **Modify any task's done state**, marking arbitrary victims' tasks done (or
  clearing it) and altering `done_at`.

Vikunja's permission model is built specifically to isolate projects between
users; this endpoint defeats that isolation. It is the same impact and class that
warranted CVEs for task relations, attachments and comments.

---

## Suggested fix

In `TaskBucket.CanUpdate`, after the bucket/project check, also verify the caller's
permission on the body-supplied task — mirroring the remediation already applied
to task relations and attachments:

    task := &Task{ID: b.TaskID}
    canUpdateTask, err := task.CanUpdate(s, a)
    if err != nil || !canUpdateTask {
        return false, err
    }

(Use `CanRead` if moving a readable-but-not-writable task into a bucket is intended;
`CanUpdate` is the safer default since the operation can change the task's done
state.)

---

## References

- CWE-639 Authorization Bypass Through User-Controlled Key
- CWE-284 Improper Access Control
- OWASP A01:2021 Broken Access Control
- CVE-2026-33676, CVE-2026-33678, CVE-2026-33313, CVE-2026-35598 — the same
  missing-authorization-on-task-child class, already remediated; this report is
  the un-remediated `TaskBucket` sibling.

## Additional notes

- **The v2 API is affected too.** The same endpoint is exposed under `/api/v2/...`,
  and both versions route through the shared model `TaskBucket.CanUpdate` /
  `updateTaskBucket` in `pkg/models/kanban_task_bucket.go`. A model-level fix
  closes v1 and v2 simultaneously; the regression test should assert both.

- **Two fix altitudes.** The minimal fix checks the body-supplied `task_id` in
  `TaskBucket.CanUpdate` (`task.CanUpdate`/`CanRead`). A broader fix makes
  `Task.ReadOne` itself permission-aware, which also hardens other internal call
  paths that rely on it — higher blast radius, weigh accordingly.

- Side effects of the cross-tenant write confirmed across reports: flipping `done`
  rewrites `done_at`/`due_date`/`start_date`/`end_date`, inserts a `task_buckets`
  row, propagates done-state to other kanban views with a done bucket in the
  victim's project, and triggers `updateDone` rescheduling for repeating tasks.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-5pg6-m483-7vrg
- https://github.com/go-vikunja/vikunja/pull/3239
- https://github.com/go-vikunja/vikunja/commit/36cdc2ce2be0b8ccc74227d178b92047d59cd65f
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.4.0
