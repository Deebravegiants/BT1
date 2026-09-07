# [M] wger: trainer_login open redirect - ?next= parameter not validated against host

## Summary
Severity: Medium
Advisory: GHSA-vqv8-j3mj-wjxj
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-vqv8-j3mj-wjxj
Type: github-advisory

## Affected
- PyPI: `wger` — affected >=0 <2.6

## Details
### Summary

The `trainer_login` view in wger redirects to `request.GET['next']` directly via `HttpResponseRedirect()` without calling `url_has_allowed_host_and_scheme()`. After the trainer successfully enters impersonation mode, their browser is redirected to any attacker-controlled URL supplied in the `?next=` parameter, enabling Referer exfiltration and phishing.

### Details

**File**: `wger/core/views/user.py`, approximately line 203

```python
# VULNERABLE - wger/core/views/user.py
if not own:
    request.session['trainer.identity'] = orig_user_pk
    if request.GET.get('next'):
        return HttpResponseRedirect(request.GET['next'])   # no host/scheme validation
```

After the impersonation logic succeeds, the view performs no validation of the `next` parameter before issuing the redirect. An attacker who can deliver a crafted link (e.g. `/en/user/2/trainer-login?next=https://evil.example/steal`) to a trainer can redirect the trainer's browser to any external host immediately after the impersonation session is established. The `Location` header contains the raw attacker-controlled URL.

**Affected endpoint**:
- `GET /en/user/<user_pk>/trainer-login` -> `wger.core.views.user.trainer_login` (the `?next=` redirect branch)

**Suggested patch**:

```diff
--- a/wger/core/views/user.py
+++ b/wger/core/views/user.py
+from django.utils.http import url_has_allowed_host_and_scheme
+
 if not own:
     request.session['trainer.identity'] = orig_user_pk
-    if request.GET.get('next'):
-        return HttpResponseRedirect(request.GET['next'])
+    next_url = request.GET.get('next')
+    if next_url and url_has_allowed_host_and_scheme(
+        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
+    ):
+        return HttpResponseRedirect(next_url)
     return HttpResponseRedirect(reverse('core:index'))
```

Adding `@require_POST` to `trainer_login` (see also VULN-030) moves the `next` parameter to the POST body where CSRF protection applies and eliminates the combined CSRF + open-redirect attack surface entirely.

### PoC

Tested on `wger/server:latest` Docker image. Victim: `trainer1` (`gym.gym_trainer` permission).

Step 1 - Authenticate as trainer:

```
POST /en/user/login HTTP/1.1
Host: target
Content-Type: application/x-www-form-urlencoded

username=trainer1&password=[REDACTED]&csrfmiddlewaretoken=[REDACTED]

-> 302 Found; Set-Cookie: sessionid=[trainer1_session]
```

Step 2 - Trainer clicks (or is delivered) the crafted link:

```
GET /en/user/2/trainer-login?next=https://evil.example/steal HTTP/1.1
Host: target
Cookie: sessionid=[trainer1_session]

-> 302 Found
   Location: https://evil.example/steal
```

Step 3 - Attacker server logs Referer:

```
Referer: http://target/en/user/2/trainer-login?next=https://evil.example/steal
(victim user_pk and next URL exposed)
```

Reproducibility: 2/2 runs.

### Impact

An attacker who can deliver a crafted URL to a trainer (phishing email, malicious gym management system integration, social engineering) can redirect the trainer's browser to an attacker-controlled domain after the trainer enters impersonation mode. The redirect leaks:

- The wger URL structure (including the impersonated user's `user_pk`) via the browser `Referer` header.
- The session-rebound cookie (if the attacker page subsequently triggers an authenticated request with `credentials: 'include'` targeting wger, any same-site cookie without SameSite=Strict is attached).

Combined with the trainer-login scope bypass (submitted separately), this primitive allows an attacker to silently impersonate arbitrary `gym=None` users and then land the trainer on an attacker page for credential harvesting.

**Affected deployments**: every wger instance where `gym.gym_trainer` is delegated to non-admin users.

**Severity**: Medium (CVSS 5.4). Network-reachable, low complexity, low privilege (trainer role), requires victim interaction (click), scope change (attacker's origin).

## References
- https://github.com/wger-project/wger/security/advisories/GHSA-vqv8-j3mj-wjxj
- https://github.com/wger-project/wger
