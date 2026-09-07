# [H] Open WebUI: LDAP and OAuth First-User Race Condition Allows Multiple Admin Accounts

## Summary
Severity: High
Advisory: GHSA-h3ww-q6xx-w7x3
CVE: CVE-2026-45675
CWE: CWE-269, CWE-362
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-h3ww-q6xx-w7x3
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
## Summary

The LDAP and OAuth authentication flows use a TOCTOU (Time-of-Check-Time-of-Use) pattern for first-user admin role assignment. The regular signup handler (`signup_handler` in auths.py, line 663) was explicitly patched to prevent this race with the comment *"Insert with default role first to avoid TOCTOU race"*, but the LDAP and OAuth code paths were never updated with the same fix.

## Vulnerable Code

### LDAP (auths.py, lines 479-490)
```python
# Line 482 - CHECK: is the user table empty?
role = 'admin' if not Users.has_users(db=db) else request.app.state.config.DEFAULT_USER_ROLE

# Lines 484-490 - USE: create user with the role determined above
user = Auths.insert_new_auth(
    email=email,
    password=str(uuid.uuid4()),
    name=cn,
    role=role,   # <-- role was determined BEFORE insert, race window exists
    db=db,
)
```

### OAuth (oauth.py, lines 1103-1112, 1566-1574)
```python
# Line 1104 - CHECK: count users
def get_user_role(self, user, user_data):
    user_count = Users.get_num_users()
    if not user and user_count == 0:
        return 'admin'    # Line 1112

# Lines 1566-1574 - USE: create user with pre-determined role
user = Auths.insert_new_auth(
    ...
    role=self.get_user_role(None, user_data),  # Line 1571
    ...
)
```

Both paths determine the role BEFORE inserting the user, creating a race window where multiple concurrent requests on a fresh instance can all observe an empty database and all receive the `admin` role.

## Comparison with Patched Signup

The `signup_handler` (auths.py, line 663) was explicitly fixed:
```python
# Insert with default role first to avoid TOCTOU race
user = Auths.insert_new_auth(..., role=DEFAULT_USER_ROLE, ...)
# Then check if this is the only user and upgrade
if Users.get_num_users() == 1:
    Users.update_user_role_by_id(user.id, 'admin')
```

The LDAP and OAuth paths did NOT receive this fix.

## Exploitation

1. Deploy Open WebUI with LDAP or OAuth enabled on a fresh instance (no existing users)
2. Send multiple concurrent authentication requests from different users
3. Multiple requests pass the `has_users()` / `get_num_users() == 0` check simultaneously
4. All concurrent users become administrators

`DATABASE_ENABLE_SESSION_SHARING` defaults to `False` (env.py:387), so each call uses its own database session, widening the race window.

## Impact

Any LDAP/OAuth user who times their first login concurrently with the legitimate first admin can escalate to full admin privileges, gaining access to all user data, system configuration, API keys, and connected LLM backends.

## Suggested Fix

Apply the same insert-then-check pattern used in `signup_handler`: insert the user with `DEFAULT_USER_ROLE` first, then atomically check if this is the only user and upgrade to admin only if so.

## Resolution

Fixed in PR [#23626](https://github.com/open-webui/open-webui/pull/23626) (commit [96a0b3239](https://github.com/open-webui/open-webui/commit/96a0b3239b1aadb23fc359bf10849c9ba12fd6ec)), first released in **v0.9.0** (Apr 2026). Both LDAP (`routers/auths.py`) and OAuth (`utils/oauth.py`) registration paths now use the same insert-first-check-after pattern that `signup_handler` already had:

1. Insert the new user with `DEFAULT_USER_ROLE` unconditionally — no pre-insert role decision based on user count.
2. After the insert commits, atomically call `Users.get_num_users() == 1` to check whether this is the sole user.
3. Only the sole user gets promoted to `admin` via `Users.update_user_role_by_id`.

`OAuthManager.get_user_role` was also updated to return `DEFAULT_USER_ROLE` (not `admin`) for first-user bootstrap; admin promotion is deferred to the post-insert check above. With this ordering, two concurrent first-user registrations that both observe an empty table can both insert, but only one will see `get_num_users() == 1` afterward — the other will see `== 2` and not be promoted.

Users on `>= 0.9.0` are not affected.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-h3ww-q6xx-w7x3
- https://nvd.nist.gov/vuln/detail/CVE-2026-45675
- https://github.com/open-webui/open-webui/pull/23626
- https://github.com/open-webui/open-webui/commit/96a0b3239b1aadb23fc359bf10849c9ba12fd6ec
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.0
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2730.yaml
