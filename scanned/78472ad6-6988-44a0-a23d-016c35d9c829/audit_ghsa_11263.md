# [M] Vikunja has an IDOR in Task Comments Allows Reading Arbitrary Comments

## Summary
Severity: Medium
Advisory: GHSA-mr3j-p26x-72x4
CVE: CVE-2026-33313
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-mr3j-p26x-72x4
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0

## Details
An authenticated user can read any task comment by ID, regardless of whether they have access to the task the comment belongs to, by substituting the task ID in the API URL with a task they do have access to.

## Details

The `GET /api/v1/tasks/{taskID}/comments/{commentID}` endpoint performs an authorization check against the task ID provided in the URL path, then loads the comment by its own ID without verifying it belongs to that task.

### Root Cause

In `pkg/models/task_comment_permissions.go`, `CanRead` constructs a `Task` using the `TaskID` from the URL and checks `Task.CanRead`:

```go
func (tc *TaskComment) CanRead(s *xorm.Session, a web.Auth) (bool, int, error) {
    t := Task{ID: tc.TaskID}
    return t.CanRead(s, a)
}
```

In `pkg/models/task_comments.go`, `getTaskCommentSimple` loads the comment by ID only, with `NoAutoCondition()` explicitly disabling XORM's implicit struct-field filtering:

```go
func getTaskCommentSimple(s *xorm.Session, tc *TaskComment) error {
    exists, err := s.
        Where("id = ?", tc.ID).
        NoAutoCondition().
        Get(tc)
    // ...
}
```

The generic web handler (`pkg/web/handler/read_one.go`) calls `CanRead` before `ReadOne`, so the permission check passes against the attacker-controlled task ID, and then `ReadOne` returns the comment from a completely different task.

### Attack Scenario

1. Attacker is authenticated and has read access to any task (task ID `A`) — e.g. their own task.
2. Attacker guesses or enumerates a comment ID (`C`) belonging to a task in another user's private project.
3. Attacker requests: `GET /api/v1/tasks/A/comments/C`
4. Authorization passes because the attacker can read task `A`.
5. The comment `C` is loaded by ID only and returned, leaking its contents and author.

## Credit

This vulnerability was found using [GitHub Security Lab Taskflows](https://github.com/GitHubSecurityLab/seclab-taskflows).

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-mr3j-p26x-72x4
- https://nvd.nist.gov/vuln/detail/CVE-2026-33313
- https://github.com/go-vikunja/vikunja/commit/bc6d843ed4df82a6c89f10aa676a7a33d27bf2fd
- https://github.com/go-vikunja/vikunja
- https://vikunja.io/changelog/vikunja-v2.2.0-was-released
