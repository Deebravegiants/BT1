# [M] MobSF has SQL Injection in its SQLite Database Viewer Utils

## Summary
Severity: Medium
Advisory: GHSA-hqjr-43r5-9q58
CVE: CVE-2026-33545
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-hqjr-43r5-9q58
Type: github-advisory

## Affected
- PyPI: `mobsf` — affected >=0 <4.4.6

## Details
## Description

MobSF's `read_sqlite()` function in `mobsf/MobSF/utils.py` (lines 542-566) uses Python string formatting (`%`) to construct SQL queries with table names read from a SQLite database's `sqlite_master` table. When a security analyst uses MobSF to analyze a malicious mobile application containing a crafted SQLite database, attacker-controlled table names are interpolated directly into SQL queries without parameterization or escaping.

This allows an attacker to:

1. **Cause Denial of Service** -- A malicious table name causes the database viewer to crash, preventing the analyst from viewing ANY data in the SQLite database. A malicious app can use this to hide sensitive data (C2 server URLs, stolen credentials, API keys) from MobSF's analysis.

2. **Achieve SQL Injection** -- The `SELECT * FROM` query on line 557 is provably injectable via `UNION SELECT`, allowing attacker-controlled data to be returned in query results. The current code structure (a `PRAGMA` statement that runs first on line 553) limits the full exploitation chain, but the underlying code is verifiably injectable.

## Root Cause

The vulnerable code in `mobsf/MobSF/utils.py:542-566`:

```python
def read_sqlite(sqlite_file):
    """Sqlite Dump - Readable Text."""
    table_dict = {}
    try:
        con = sqlite3.connect(sqlite_file)
        cur = con.cursor()
        cur.execute('SELECT name FROM sqlite_master WHERE type=\'table\';')
        tables = cur.fetchall()
        for table in tables:
            table_dict[table[0]] = {'head': [], 'data': []}
            cur.execute('PRAGMA table_info(\'%s\')' % table)    # <-- INJECTION POINT 1
            rows = cur.fetchall()
            for sq_row in rows:
                table_dict[table[0]]['head'].append(sq_row[1])
            cur.execute('SELECT * FROM \'%s\'' % table)         # <-- INJECTION POINT 2
            rows = cur.fetchall()
            for sq_row in rows:
                tmp_row = []
                for each_row in sq_row:
                    tmp_row.append(str(each_row))
                table_dict[table[0]]['data'].append(tmp_row)
    except Exception:
        logger.exception('Reading SQLite db')
    return table_dict
```

**Lines 553 and 557** use `%` string formatting to interpolate `table` (a tuple from `sqlite_master`) directly into SQL strings. The `table` value is attacker-controlled when the SQLite database originates from a malicious application being analyzed.

## Attack Vector

The `read_sqlite()` function is called from two locations:

1. **Dynamic Analysis File Viewer** (`mobsf/DynamicAnalyzer/views/common/device.py:64`):
   - Triggered when an analyst clicks to view a `.db` file in device data
   - Applies to both Android and iOS dynamic analysis

2. **iOS Static Analysis File Viewer** (`mobsf/StaticAnalyzer/views/ios/views/view_source.py:123`):
   - Triggered when an analyst clicks to view a `.db` file during iOS static analysis

### Attack Scenario

1. Attacker creates a malicious Android APK (or iOS IPA) containing a SQLite database with a crafted table name in the `assets/` directory
2. The SQLite database contains a table created with:
   ```sql
   CREATE TABLE "x' UNION SELECT 'SQL_INJECTION_PROOF'--" (id INTEGER);
   ```
3. Security analyst uploads the application to MobSF for analysis
4. Analyst browses the extracted files and clicks to view the SQLite database
5. MobSF's `read_sqlite()` reads table names from `sqlite_master`, including the malicious name `x' UNION SELECT 'SQL_INJECTION_PROOF'--`
6. The table name is interpolated into SQL queries via string formatting:
   - `PRAGMA table_info('x' UNION SELECT 'SQL_INJECTION_PROOF'--')` -- causes syntax error (DoS)
   - `SELECT * FROM 'x' UNION SELECT 'SQL_INJECTION_PROOF'--'` -- SQL injection (UNION SELECT returns attacker data)

## Impact

### Denial of Service (Confirmed)

When the malicious table name is the first table in `sqlite_master` (i.e., created first in the database), the `PRAGMA` statement on line 553 raises a `sqlite3.OperationalError`, which is caught by the outer `try/except`. This causes `read_sqlite()` to return an empty or partial result, preventing the analyst from viewing **any** database content.

**Security impact:** A malicious app author can use this technique to **hide incriminating data** stored in SQLite databases from MobSF's analysis. This directly undermines MobSF's core purpose as a security analysis tool.

### SQL Injection (Confirmed in Isolation)

The `SELECT * FROM` query on line 557 is demonstrably injectable. When the malicious table name `x' UNION SELECT 'SQL_INJECTION_PROOF'--` is interpolated, the resulting query:

```sql
SELECT * FROM 'x' UNION SELECT 'SQL_INJECTION_PROOF'--'
```

Successfully executes and returns attacker-controlled data via `UNION SELECT`. The `--` comments out the trailing single quote. This is verified by the PoC script.

**Note:** In the current code structure, the `PRAGMA table_info()` statement on line 553 runs before the `SELECT * FROM` on line 557. The PRAGMA fails with a syntax error for injected payloads, which triggers the exception handler before the SELECT can execute. This limits the full exploitation chain. However, the code flaw is real and any future refactoring that changes the execution order or removes the PRAGMA would immediately expose the full SQL injection.

## Proof of Concept

### Files Provided(Gdrive)

| File | Description |
|------|-------------|
| `poc_sqlite_injection.py` | Standalone PoC demonstrating the vulnerability |
| `malicious.db` | Crafted SQLite database (generated by PoC) |
| `create_malicious_apk.sh` | Script to package the malicious DB into an APK |
| `malicious_sqli.apk` | Pre-built APK for testing against MobSF |

https://drive.google.com/drive/folders/1mNGkFfNowkaZ5J018HFi4IQcnjKaWCym?usp=sharing


### Running the PoC

```bash
# Run the standalone PoC (no MobSF required)
python3 poc_sqlite_injection.py

# Build the malicious APK (requires Android SDK)
./create_malicious_apk.sh

# Test against MobSF
# 1. Start MobSF
# 2. Upload malicious_sqli.apk
# 3. Browse extracted files -> click app_data.db
# 4. Observe: database viewer fails (DoS)
```

### PoC Output (Abbreviated)

```
[STEP 2] Running MobSF's read_sqlite() against malicious database...
    [!] EXCEPTION CAUGHT: OperationalError: near "UNION": syntax error
    [!] DoS CONFIRMED: read_sqlite() crashed

[STEP 3] Demonstrating SELECT * FROM injection in isolation...
    Query: SELECT * FROM 'x' UNION SELECT 'SQL_INJECTION_PROOF'--'
    [+] Query executed successfully!
    [+] Results: [('SQL_INJECTION_PROOF',), ('normal_data',)]
    [+] SQL INJECTION CONFIRMED

[STEP 4] Complete DoS (malicious table created first):
    Tables with data: NONE
    [!] COMPLETE DoS CONFIRMED
```

## Suggested Fix

Replace string formatting with properly quoted identifiers. SQLite uses double quotes for identifiers:

```python
def read_sqlite(sqlite_file):
    """Sqlite Dump - Readable Text."""
    table_dict = {}
    try:
        con = sqlite3.connect(sqlite_file)
        cur = con.cursor()
        cur.execute('SELECT name FROM sqlite_master WHERE type=\'table\';')
        tables = cur.fetchall()
        for table in tables:
            table_name = table[0]
            # Properly escape table name as a double-quoted identifier
            safe_name = table_name.replace('"', '""')
            table_dict[table_name] = {'head': [], 'data': []}
            cur.execute(f'PRAGMA table_info("{safe_name}")')
            rows = cur.fetchall()
            for sq_row in rows:
                table_dict[table_name]['head'].append(sq_row[1])
            cur.execute(f'SELECT * FROM "{safe_name}"')
            rows = cur.fetchall()
            for sq_row in rows:
                tmp_row = []
                for each_row in sq_row:
                    tmp_row.append(str(each_row))
                table_dict[table_name]['data'].append(tmp_row)
    except Exception:
        logger.exception('Reading SQLite db')
    return table_dict
```

This escapes any double quotes within table names by doubling them (`"` → `""`), which is the standard SQL mechanism for identifier quoting. This prevents breakout from the double-quoted identifier context.

## Resources

- **CWE-89**: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')
- **OWASP SQL Injection**: https://owasp.org/www-community/attacks/SQL_Injection
- **Affected File**: `mobsf/MobSF/utils.py`, lines 542-566

## References
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/security/advisories/GHSA-hqjr-43r5-9q58
- https://nvd.nist.gov/vuln/detail/CVE-2026-33545
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/6f8a43c1b78d21cfbd7186aaafa7f622d990e0f1
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/releases/tag/v4.4.6
