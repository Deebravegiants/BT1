# [M] Lemur Privilege Escalation: Non-admin role members can rewrite role membership via PUT /api/1/roles/<id>

## Summary
Severity: Medium
Advisory: GHSA-x3vf-mgxj-7785
CVE: CVE-2026-55163
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-x3vf-mgxj-7785
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0 <1.9.2

## Details
## Summary
 
The `PUT /api/1/roles/<id>` handler in `lemur/roles/views.py` gates only on `RoleMemberPermission(role_id).can()`, which is satisfied for any user who is already a member of the target role. The handler then passes `data["users"]` and `data["name"]` directly to `service.update()`, permitting any role member to rewrite that role's membership list and name. The companion `DELETE` handler on the same resource is correctly gated by `@admin_permission.require`; the asymmetry between PUT and DELETE on identical resources indicates an authorization oversight rather than a deliberate design choice.
 
## Root Cause
 
`lemur/roles/views.py:298`:
 
```python
permission = RoleMemberPermission(role_id)
if permission.can():
    return service.update(
        role_id, data["name"], data.get("description"), data.get("users")
    )
return dict(message="You are not authorized to modify this role."), 403
 
@admin_permission.require(http_exception=403)
def delete(self, role_id):
    ...
```
 
`lemur/auth/permissions.py:56`:
 
```python
class RoleMemberPermission(Permission):
    def __init__(self, role_id):
        needs = [RoleNeed("admin"), RoleMemberNeed(role_id)]
        super().__init__(*needs)
```
 
`flask_principal.Permission.allows()` is OR-semantic across needs, so `RoleMemberPermission(role_id).can()` returns `True` if the caller is either an admin **or** a member of `role_id`. The PUT handler treats membership-of-self as sufficient to mutate the role; DELETE does not.
 
## Affected Endpoints
 
| Method | Path | Source |
|---|---|---|
| PUT | /api/1/roles/`<id>` | lemur/roles/views.py:298 |
 
## Impact
 
A user who is a member of role X can:
 
- **Add other users to role X**, granting them whatever certificate/authority access role X confers. In installs that delegate certificate or authority ownership to non-admin roles, this promotes arbitrary users to peer of every other role member.
- **Remove other users from role X**, denying their access (availability / governance impact).
- **Rename role X** to an arbitrary string.
The "rename to admin" path is blocked by the `unique=True` constraint on `Role.name` and by strict equality in `User.is_admin`, so direct self-promotion to admin via rename is not possible on default installs. The principal exploitation surface is membership rewriting and lateral promotion of colluders within roles the attacker already belongs to.
 
## Remediation
 
Add `@admin_permission.require(http_exception=403)` to `Roles.put`, mirroring the existing decorator on `Roles.delete`:
 
```python
@admin_permission.require(http_exception=403)
def put(self, role_id, data=None):
    ...
```
 
If selective delegation is intended (role owners managing their own roles), that capability should be modeled with a dedicated permission class whose Needs reflect role *ownership* rather than membership, and the `name` field should be excluded from the mutable schema on that delegated path.
 
## Steps to Reproduce
 
1. Set up Lemur with default configuration. Create an admin user `admin`, and two non-admin users `alice` and `bob`. Add `alice` to the built-in `operator` role; leave `bob` with no roles or with `read-only` only.
2. Authenticate as `alice` and capture the JWT:
   ```
   curl -X POST https://lemur.local/api/1/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username":"alice","password":"<alice_pw>"}'
   ```
 
3. Confirm the initial state - `bob` is not a member of `operator`:
   ```
   curl https://lemur.local/api/1/roles?filter=name;operator \
        -H "Authorization: Bearer <admin_jwt>"
   # observe: alice present in users list, bob absent
   ```
 
4. As `alice`, send a PUT that injects `bob` into the `operator` role:
   ```
   curl -X PUT https://lemur.local/api/1/roles/<operator_role_id> \
        -H "Authorization: Bearer <alice_jwt>" \
        -H "Content-Type: application/json" \
        -d '{
              "name": "operator",
              "description": "modified by alice",
              "users": [{"id": <alice_id>}, {"id": <bob_id>}]
            }'
   # observe: HTTP 200
   ```
 
5. Confirm `bob` is now a member of `operator`:
   ```
   curl https://lemur.local/api/1/roles?filter=name;operator \
        -H "Authorization: Bearer <admin_jwt>"
   # observe: bob now present in users list
   ```
 
Step 4 succeeds despite `alice` not being an admin. The same handler also accepts a `name` field; substituting `"name": "operator_v2"` in step 4 renames the role, demonstrating the second variant of the bug.

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-x3vf-mgxj-7785
- https://github.com/Netflix/lemur
- https://github.com/Netflix/lemur/releases/tag/v1.9.2
