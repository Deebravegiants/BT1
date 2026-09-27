# [M] Lemur user-update path stores plaintext passwords

## Summary
Severity: Medium
Advisory: GHSA-q437-g7fv-2jvv
CVE: CVE-2026-55164
CWE: CWE-256
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-q437-g7fv-2jvv
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0 <1.9.2

## Details
## Summary

`lemur.users.service.update()` writes a user's new password as plaintext to the `users.password` column. The `User` model wires bcrypt hashing to SQLAlchemy's `before_insert` event but registers no equivalent listener for `before_update`, and `service.update()` does not call `user.hash_password()` after assigning the new value. Every password change performed through the admin-gated `PUT /api/1/users/<id>` endpoint persists the user's password to the database in cleartext.

## Root Cause

`lemur/users/models.py`:

```python
# line 38
class User(BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    password = Column(String(128))            # plain column, no setter, no Vault descriptor

# line 74
    def hash_password(self):
        if self.password:
            self.password = bcrypt.generate_password_hash(self.password).decode("utf-8")

# line 111
listen(User, "before_insert", hash_password)  # only before_insert is wired
```

`lemur/users/service.py`:

```python
# line 46
def update(user_id, username, email, active, profile_picture, roles, password=None):
    ...
    user = get(user_id)
    user.username = username
    user.email = email
    user.active = active
    user.profile_picture = profile_picture
    if password:
        user.password = password              # raw assignment
    update_roles(user, roles)
    return database.update(user)              # commits, no hashing
```

No `before_update` listener exists. `User.password` is a plain `Column(String(128))` with no property setter that hashes on assignment. The bcrypt code path is bypassed entirely on every UPDATE statement that touches this column.

## Affected Endpoints

| Method | Path | Source |
|---|---|---|
| PUT | /api/1/users/`<id>` | lemur/users/views.py:274 (gated by `@admin_permission.require`) |

`lemur/auth/views.py:323` also calls `user_service.update()` during SSO/OAuth login, but passes only six positional arguments. `password` defaults to `None` on that path and the `if password:` guard short-circuits. The bug is triggered only through the admin-only PUT handler.

## Impact

When an administrator changes a user's password via `PUT /api/1/users/<id>`, the cleartext password is persisted to `users.password`. Subsequent login attempts for that user will fail (`check_password` calls `bcrypt.check_password_hash` against an unhashed value), pushing operators toward workarounds.

The more serious consequence is a defense-in-depth bypass. Bcrypt is the protection that prevents a database compromise from yielding usable credentials. With plaintext rows present, an attacker who exfiltrates the `users` table, a backup, a read replica, or query logs obtains directly usable login credentials — no offline cracking required. Because users reuse passwords across services, the blast radius extends beyond Lemur.

The bug specifically affects admin-driven password resets, which are the normal post-incident workflow and exactly when plaintext storage is most harmful.

## Steps to Reproduce

1. Install Lemur with default config. Create an admin user and a target user 'alice' (created via the standard flow, password will be hashed correctly on insert).

2. Verify the initial hash:
   psql lemur -c "SELECT password FROM users WHERE username='alice';"
   # Output: $2b$12$N9Q...   (bcrypt hash, as expected)

3. As admin, change alice's password via the API:
   curl -X PUT https://lemur.local/api/1/users/<alice_id> \
        -H "Authorization: Bearer <admin_jwt>" \
        -H "Content-Type: application/json" \
        -d '{
          "username": "alice",
          "email": "alice@example.com",
          "active": true,
          "profile_picture": null,
          "roles": [{"name": "operator"}],
          "password": "ProofOfConcept_2026"
        }'

4. Read the column again:
   psql lemur -c "SELECT password FROM users WHERE username='alice';"
   # Output: ProofOfConcept_2026   ← plaintext, not hashed

5. Confirm the failure mode: 'alice' can no longer log in with 'ProofOfConcept_2026'
   because check_password runs bcrypt.check_password_hash() against the cleartext column.


## Remediation

Register the listener for both events:

```python
# lemur/users/models.py
listen(User, "before_insert", hash_password)
listen(User, "before_update", hash_password)
```

Alternative, equivalent fix in the service layer:

```python
# lemur/users/service.py, in update()
    if password:
        user.password = password
        user.hash_password()
```

The listener fix is preferred because it closes the gap for any future code path that mutates `user.password`.

A one-time migration is recommended to detect and re-hash any rows already stored in cleartext. Bcrypt hashes begin with `$2b$`, `$2a$`, or `$2y$`. Any cleartext credential should be treated as **compromised** — rotate it, do not just re-hash it — since it has been at rest in plaintext and may exist in backups, audit logs, and replicas.

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-q437-g7fv-2jvv
- https://github.com/Netflix/lemur
- https://github.com/Netflix/lemur/releases/tag/v1.9.2
