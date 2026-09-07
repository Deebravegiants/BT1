# [M] Vikunja has Cross-Project Information Disclosure via Task Relations — Missing Authorization Check on Related Task Read

## Summary
Severity: Medium
Advisory: GHSA-8cmm-j6c4-rr8v
CVE: CVE-2026-33676
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-8cmm-j6c4-rr8v
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.2.1

## Details
## Summary

When the Vikunja API returns tasks, it populates the `related_tasks` field with full task objects for all related tasks without checking whether the requesting user has read permission on those tasks' projects. An authenticated user who can read a task that has cross-project relations will receive full details (title, description, due dates, priority, percent completion, project ID, etc.) of tasks in projects they have no access to.

## Details

The vulnerability is in `addRelatedTasksToTasks()` at `pkg/models/tasks.go:496-548`. This function is called by `addMoreInfoToTasks()` (line 773) during every task read operation — both project task listings (`GET /api/v1/projects/{id}/views/{id}/tasks`) and single task reads (`GET /api/v1/tasks/{id}`).

The function fetches all related tasks directly from the database without any permission filtering:

```go
// pkg/models/tasks.go:496-548
func addRelatedTasksToTasks(s *xorm.Session, taskIDs []int64, taskMap map[int64]*Task, a web.Auth) (err error) {
    relatedTasks := []*TaskRelation{}
    err = s.In("task_id", taskIDs).Find(&relatedTasks)
    // ...
    fullRelatedTasks := make(map[int64]*Task)
    err = s.In("id", relatedTaskIDs).Find(&fullRelatedTasks)  // Line 514: NO permission check
    // ...
    for _, rt := range relatedTasks {
        // Directly adds to response without checking if user can read the related task
        taskMap[rt.TaskID].RelatedTasks[rt.RelationKind] = append(
            taskMap[rt.TaskID].RelatedTasks[rt.RelationKind], otherTask)
    }
}
```

The `a web.Auth` parameter is received but only used for determining favorites (line 519), never for access control on the related tasks themselves.

In contrast, `addBucketsToTasks()` (line 550+) in the same file correctly filters enrichment data by calling `getAllRawProjects(s, a, ...)` to scope results to projects the requesting user can access.

While task relation **creation** properly enforces authorization (`task_relation_permissions.go:32-52` checks write access on the base task and read access on the other task), the relation **display** path does not re-check permissions for the current reader. This means a privileged user can create a relation that then leaks data to all other users who can read the base task.

## PoC

**Setup:** Two users (User A, User B), two projects (Project-Shared, Project-Private).
- User A has access to both projects.
- User B has access only to Project-Shared.
- Task 1 exists in Project-Shared, Task 2 exists in Project-Private.

**Step 1: User A creates a relation between the two tasks**

```bash
# As User A (who has access to both projects)
curl -X PUT "http://localhost:3456/api/v1/tasks/TASK1_ID/relations" \
  -H "Authorization: Bearer USER_A_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"other_task_id": TASK2_ID, "relation_kind": "related"}'
```

Expected: 201 Created (User A has write on Task 1, read on Task 2).

**Step 2: User B reads tasks from the shared project**

```bash
# As User B (who has NO access to Project-Private)
curl "http://localhost:3456/api/v1/projects/PROJECT_SHARED_ID/views/VIEW_ID/tasks" \
  -H "Authorization: Bearer USER_B_TOKEN"
```

Expected: Task 1 should be returned, but related_tasks should NOT include Task 2.

**Actual result:** The response includes Task 1 with the `related_tasks` field containing the full Task 2 object, including its `title`, `description`, `due_date`, `priority`, `percent_done`, `project_id`, and other metadata — despite User B having no access to Project-Private.

## Impact

- **Information disclosure**: Any authenticated user can read the full metadata of tasks in projects they do not have access to, as long as a relation exists from a task they can read.
- **Leaked fields include**: title, description, due dates, start dates, priority, percent completion, project ID, hex color, task index, done status, repeat configuration, cover image attachment ID, and creation/update timestamps.
- **Project structure disclosure**: The `project_id` field reveals the existence and IDs of private projects.
- **No user interaction required**: Once a privileged user creates a cross-project relation (which is intentionally allowed), the data leak is automatic for all readers of the base task.
- **Blast radius**: Affects all Vikunja instances with cross-project task relations. In multi-tenant or team environments where projects have different access scopes, this undermines project-level access control.

## Recommended Fix

Filter related tasks by the requesting user's read permissions before adding them to the response. In `addRelatedTasksToTasks()`, after fetching full task objects, check that the user can read each related task's project:

```go
func addRelatedTasksToTasks(s *xorm.Session, taskIDs []int64, taskMap map[int64]*Task, a web.Auth) (err error) {
    relatedTasks := []*TaskRelation{}
    err = s.In("task_id", taskIDs).Find(&relatedTasks)
    if err != nil {
        return
    }

    var relatedTaskIDs []int64
    for _, rt := range relatedTasks {
        relatedTaskIDs = append(relatedTaskIDs, rt.OtherTaskID)
    }

    if len(relatedTaskIDs) == 0 {
        return
    }

    fullRelatedTasks := make(map[int64]*Task)
    err = s.In("id", relatedTaskIDs).Find(&fullRelatedTasks)
    if err != nil {
        return
    }

    // Filter related tasks by user's read permission
    allowedProjectIDs := make(map[int64]bool)
    checkedProjectIDs := make(map[int64]bool)
    for _, t := range fullRelatedTasks {
        if checkedProjectIDs[t.ProjectID] {
            continue
        }
        checkedProjectIDs[t.ProjectID] = true
        p := &Project{ID: t.ProjectID}
        canRead, _, err := p.CanRead(s, a)
        if err != nil {
            log.Errorf("Could not check project read permission: %v", err)
            continue
        }
        if canRead {
            allowedProjectIDs[t.ProjectID] = true
        }
    }

    taskFavorites, err := getFavorites(s, relatedTaskIDs, a, FavoriteKindTask)
    if err != nil {
        return err
    }

    for _, rt := range relatedTasks {
        task, has := fullRelatedTasks[rt.OtherTaskID]
        if !has {
            continue
        }
        // Skip related tasks the user cannot access
        if !allowedProjectIDs[task.ProjectID] {
            continue
        }
        fullRelatedTasks[rt.OtherTaskID].IsFavorite = taskFavorites[rt.OtherTaskID]
        otherTask := &Task{}
        err = copier.Copy(otherTask, fullRelatedTasks[rt.OtherTaskID])
        if err != nil {
            log.Errorf("Could not duplicate task object: %v", err)
            continue
        }
        otherTask.RelatedTasks = nil
        taskMap[rt.TaskID].RelatedTasks[rt.RelationKind] = append(
            taskMap[rt.TaskID].RelatedTasks[rt.RelationKind], otherTask)
    }

    return
}
```

This checks project-level read permission once per unique project ID (cached in `allowedProjectIDs`) and skips related tasks from projects the user cannot access.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-8cmm-j6c4-rr8v
- https://nvd.nist.gov/vuln/detail/CVE-2026-33676
- https://github.com/go-vikunja/vikunja/pull/2449
- https://github.com/go-vikunja/vikunja/commit/833f2aec006ac0f6643c41872e45dd79220b9174
- https://github.com/go-vikunja/vikunja
- https://vikunja.io/changelog/vikunja-v2.2.2-was-released
