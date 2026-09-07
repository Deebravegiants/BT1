# [H] Glances has a SQL Injection in DuckDB Export via Unparameterized DDL Statements

## Summary
Severity: High
Advisory: GHSA-49g7-2ww7-3vf5
CVE: CVE-2026-32611
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-49g7-2ww7-3vf5
Type: github-advisory

## Affected
- PyPI: `Glances` — affected >=0 <4.5.2

## Details
## Summary

The GHSA-x46r fix (commit 39161f0) addressed SQL injection in the TimescaleDB export module by converting all SQL operations to use parameterized queries and `psycopg.sql` composable objects. However, the DuckDB export module (`glances/exports/glances_duckdb/__init__.py`) was not included in this fix and contains the same class of vulnerability: table names and column names derived from monitoring statistics are directly interpolated into SQL statements via f-strings. While DuckDB INSERT values already use parameterized queries (`?` placeholders), the DDL construction and table name references do not escape or parameterize identifier names.

## Details

The DuckDB export module constructs SQL DDL statements by directly interpolating stat field names and plugin names into f-strings.

**Vulnerable CREATE TABLE construction** (`glances/exports/glances_duckdb/__init__.py:156-162`):

```python
create_query = f"""
CREATE TABLE {plugin} (
{', '.join(creation_list)}
);"""
self.client.execute(create_query)
```

The `creation_list` is built from stat dictionary keys in the `update()` method (`glances/exports/glances_duckdb/__init__.py:117-118`):

```python
for key, value in plugin_stats.items():
    creation_list.append(f"{key} {convert_types[type(self.normalize(value)).__name__]}")
```

The INSERT statement also uses the unescaped `plugin` name (`glances/exports/glances_duckdb/__init__.py:172-174`):

```python
insert_query = f"""
INSERT INTO {plugin} VALUES (
{', '.join(['?' for _ in values])}
);"""
```

While INSERT values use `?` placeholders (safe), the table name `{plugin}` is directly interpolated in both CREATE TABLE and INSERT INTO statements. Column names in creation_list are also directly interpolated without quoting.

**Comparison with the TimescaleDB fix (commit 39161f0):**

The TimescaleDB fix addressed this exact pattern by:
1. Using `psycopg.sql.Identifier()` for table and column names
2. Using `psycopg.sql.SQL()` for composing queries
3. Using `%s` placeholders for all values

The DuckDB module was not part of this fix despite having the same vulnerability class.

**Attack vector:**

The primary attack vector is through stat dictionary keys. While most keys come from hardcoded psutil field names (e.g., `cpu_percent`, `memory_usage`), any future plugin that introduces dynamic keys from external data (container labels, custom metrics, user-defined sensor names) would create an exploitable injection path. Additionally, the table name (`plugin`) comes from the internal plugins list, but any custom plugin with a crafted name could inject SQL.

## PoC

The injection is demonstrable when column or table names contain SQL metacharacters:

```python
# Simulated injection via a hypothetical plugin with dynamic keys
# If a stat dict contained a key like:
#   "cpu_percent BIGINT); DROP TABLE cpu; --"
# The creation_list would produce:
#   "cpu_percent BIGINT); DROP TABLE cpu; -- VARCHAR"
# Which in the CREATE TABLE f-string becomes:
#   CREATE TABLE plugin_name (
#     time TIMETZ,
#     hostname_id VARCHAR,
#     cpu_percent BIGINT); DROP TABLE cpu; -- VARCHAR
#   );
```

```bash
# Verify with DuckDB export enabled:
# 1. Configure DuckDB export in glances.conf:
# [duckdb]
# database=/tmp/glances.duckdb

# 2. Start Glances with DuckDB export and debug logging
glances --export duckdb --debug 2>&1 | grep "Create table"

# 3. Observe the unescaped SQL in debug output
```

## Impact

- **Defense-in-depth gap:** The identical vulnerability pattern was identified and fixed in TimescaleDB (GHSA-x46r) but the fix was not applied to the sibling DuckDB module. This represents an incomplete patch that leaves the same attack surface open through a different code path.

- **Future exploitability:** If any Glances plugin is added or modified to produce stat dictionary keys from external/user-controlled data (e.g., container metadata, custom metric names, SNMP OID labels), the DuckDB export would become immediately exploitable for SQL injection without any additional code changes.

- **Data integrity:** A successful injection in the CREATE TABLE statement could corrupt the DuckDB database, create unauthorized tables, or modify schema in ways that affect other applications reading from the same database file.

## Recommended Fix

Apply the same parameterization approach used in the TimescaleDB fix. DuckDB supports identifier quoting with double quotes:

```python
# glances/exports/glances_duckdb/__init__.py

def _quote_identifier(name):
    """Quote a SQL identifier to prevent injection."""
    # DuckDB uses double-quote escaping for identifiers
    return '"' + name.replace('"', '""') + '"'

def export(self, plugin, creation_list, values_list):
    """Export the stats to the DuckDB server."""
    logger.debug(f"Export {plugin} stats to DuckDB")

    table_list = [t[0] for t in self.client.sql("SHOW TABLES").fetchall()]
    if plugin not in table_list:
        # Quote table and column names to prevent injection
        quoted_plugin = _quote_identifier(plugin)
        quoted_fields = []
        for item in creation_list:
            parts = item.split(' ', 1)
            col_name = _quote_identifier(parts[0])
            col_type = parts[1] if len(parts) > 1 else 'VARCHAR'
            quoted_fields.append(f"{col_name} {col_type}")

        create_query = f"CREATE TABLE {quoted_plugin} ({', '.join(quoted_fields)});"
        try:
            self.client.execute(create_query)
        except Exception as e:
            logger.error(f"Cannot create table {plugin}: {e}")
            return

    self.client.commit()

    # Insert with quoted table name
    quoted_plugin = _quote_identifier(plugin)
    for values in values_list:
        insert_query = f"INSERT INTO {quoted_plugin} VALUES ({', '.join(['?' for _ in values])});"
        try:
            self.client.execute(insert_query, values)
        except Exception as e:
            logger.error(f"Cannot insert data into table {plugin}: {e}")

    self.client.commit()
```

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-49g7-2ww7-3vf5
- https://nvd.nist.gov/vuln/detail/CVE-2026-32611
- https://github.com/nicolargo/glances/commit/63b7da28895249d775202d639e5531ba63491a5c
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.2
