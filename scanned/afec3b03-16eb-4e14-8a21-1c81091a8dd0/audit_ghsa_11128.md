# [H] Glances has SQL Injection via Process Names in TimescaleDB Export

## Summary
Severity: High
Advisory: GHSA-x46r-mf5g-xpr6
CVE: CVE-2026-30930
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-x46r-mf5g-xpr6
Type: github-advisory

## Affected
- PyPI: `Glances` — affected >=0 <4.5.1

## Details
### Summary

The TimescaleDB export module constructs SQL queries using string concatenation with unsanitized system monitoring data. The normalize() method wraps string values in single quotes but does not escape embedded single quotes, making SQL injection trivial via attacker-controlled data such as process names, filesystem mount points, network interface names, or container names.

Root Cause: The normalize() function uses f"'{value}'" for string values without escaping single quotes within the value. The resulting strings are concatenated into INSERT queries via string formatting and executed directly with cur.execute() — no parameterized queries are used.

#### Affected Code
- _File: glances/exports/glances_timescaledb/__init__.py, lines 79-93 (normalize function)_
```
def normalize(self, value):
    """Normalize the value to be exportable to TimescaleDB."""
    if value is None:
        return 'NULL'
    if isinstance(value, bool):
        return str(value).upper()
    if isinstance(value, (list, tuple)):
        # Special case for list of one boolean
        if len(value) == 1 and isinstance(value[0], bool):
            return str(value[0]).upper()
        return ', '.join([f"'{v}'" for v in value])
    if isinstance(value, str):
        return f"'{value}'"  # <-- NO ESCAPING of single quotes within value

    return f"{value}"
```

- _File: glances/exports/glances_timescaledb/__init__.py, lines 201-205 (query construction)_
```
# Insert the data
insert_list = [f"({','.join(i)})" for i in values_list]
insert_query = f"INSERT INTO {plugin} VALUES {','.join(insert_list)};"
logger.debug(f"Insert data into table: {insert_query}")
try:
    cur.execute(insert_query)  # <-- Direct execution of concatenated SQL
```

### PoC
- As a normal user, create a process with the name containing the SQL Injection payload:
```
exec -a "x'); COPY (SELECT version()) TO '/tmp/sqli_proof.txt' --"   python3 -c 'import time; [sum(range(500000)) or time.sleep(0.01) for _ in iter(int, 1)]'
```
- Start Glances with TimescaleDB export as root user:
```
glances --export timescaledb --export-process-filter ".*" --time 5 --stdout cpu
```
- Observe that sqli_proof.txt is created in /tmp directory.

### Impact

- Data Destruction: DROP TABLE, DELETE, TRUNCATE operations against the TimescaleDB database.
- Data Exfiltration: Using COPY ... TO or subqueries to extract data from other tables.
- Potential RCE: Via PostgreSQL extensions like COPY ... PROGRAM which executes OS commands.
- Privilege Escalation: Any local user who can create a process with a crafted name can inject SQL into the database, potentially compromising the entire PostgreSQL instance.

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-x46r-mf5g-xpr6
- https://nvd.nist.gov/vuln/detail/CVE-2026-30930
- https://github.com/nicolargo/glances/commit/39161f0d6fd723d83f534b48f24cdca722573336
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.1
