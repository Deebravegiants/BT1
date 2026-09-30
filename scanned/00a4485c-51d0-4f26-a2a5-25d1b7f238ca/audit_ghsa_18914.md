# [H] OpenSTAManager has Authenticated SQL Injection in API via 'display' parameter

## Summary
Severity: High
Advisory: GHSA-2jm2-2p35-rp3j
CVE: CVE-2025-65103
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-19
Source: https://github.com/advisories/GHSA-2jm2-2p35-rp3j
Type: github-advisory

## Affected
- Packagist: `devcode-it/openstamanager` — affected >=0 <2.9.5

## Details
### Summary
An authenticated SQL Injection vulnerability in the API allows any user, regardless of permission level, to execute arbitrary SQL queries. By manipulating the `display` parameter in an API request, an attacker can exfiltrate, modify, or delete any data in the database, leading to a full system compromise.

### Details
The vulnerability is located in the `retrieve()` method within `src/API/Manager.php`.

User input from the `display` GET parameter is processed without proper validation. The code strips the surrounding brackets `[]`, splits the string by commas, and then passes each resulting element directly into the `selectRaw()` function of the query builder.

```php
// User input from 'display' is taken without sanitization.
$select = !empty($request['display']) ? explode(',', substr((string) $request['display'], 1, -1)) : null;

// ...

// The unsanitized input is passed directly to `selectRaw()`.
foreach ($select as $s) {
    $query->selectRaw($s);
}
```

Since `selectRaw()` is designed to execute raw SQL expressions, it executes any malicious SQL code provided in the `display` parameter.

### PoC
1.  Log in to an OpenSTAManager instance as any user.
2.  Navigate to the user's profile page to obtain their personal API Token.
3.  Use this API token to send a specially crafted GET request to the API endpoint.

**Time-Based Blind Injection Test:**

Replace `<your_host>`, `<your_token>`, and `<resource_name>` with your actual values. `anagrafiche` is a valid resource.

```bash
curl "http://<your_host>/openstamanager/api?token=<your_token>&resource=anagrafiche&display=[1,SLEEP(5)]"
```

The server will delay its response by approximately 5 seconds, confirming the `SLEEP(5)` command was executed by the database.

### Impact
This is a critical SQL Injection vulnerability. Any authenticated user, even those with the lowest privileges, can exploit this vulnerability to:

*   **Exfiltrate all data** from the database (e.g., user credentials, customer information, invoices, internal data).
*   **Modify or delete data**, compromising data integrity.
*   Potentially achieve further system compromise, depending on the database user's privileges and system configuration.

## References
- https://github.com/devcode-it/openstamanager/security/advisories/GHSA-2jm2-2p35-rp3j
- https://nvd.nist.gov/vuln/detail/CVE-2025-65103
- https://github.com/devcode-it/openstamanager
