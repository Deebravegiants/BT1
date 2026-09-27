# [M] Glances has CQL Injection in its Cassandra Export Module via Unsanitized Config Values

## Summary
Severity: Medium
Advisory: GHSA-grp3-h8m8-45p7
CVE: CVE-2026-35588
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-grp3-h8m8-45p7
Type: github-advisory

## Affected
- PyPI: `glances` — affected >=0 <4.5.4

## Details
## Summary

The Cassandra export module (`glances/exports/glances_cassandra/__init__.py`) interpolates `keyspace`, `table`, and `replication_factor` configuration values directly into CQL statements without validation. A user with write access to `glances.conf` can redirect all monitoring data to an attacker-controlled Cassandra keyspace.

## Vulnerable Code

```python
# Line 80
f"CREATE KEYSPACE {self.keyspace} WITH "
f"replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '{self.replication_factor}' }}"

# Line 94
f"CREATE TABLE {self.table} (plugin text, time timeuuid, stat map<text,float>, PRIMARY KEY (plugin, time)) WITH CLUSTERING ORDER BY (time DESC)"

# Line 112
stmt = f"INSERT INTO {self.table} (plugin, time, stat) VALUES (?, ?, ?)"
```

## Steps to Reproduce

1. Configure `glances.conf` with malicious `table` value:
```ini
[cassandra]
host = 127.0.0.1
port = 9042
keyspace = glances
table = attacker_ks.captured_stats
```
2. Create attacker keyspace in Cassandra
3. Run `glances --export cassandra`
4. All monitoring data is written to `attacker_ks.captured_stats` instead of the legitimate table

**Confirmed output:**
```
INSERT stmt: INSERT INTO attacker_ks.captured_stats (plugin, time, stat) VALUES (?, ?, ?)
Legitimate table row count: 0
Attacker table row count: 1
[CONFIRMED] plugin=cpu, stat={'user': 50.0}
```

## Impact

All exported monitoring data (CPU, memory, network, disk I/O) is silently redirected to an attacker-controlled Cassandra keyspace — both data exfiltration and data loss.

## Proposed Fix

```python
import re

def _validate_cql_identifier(name: str) -> str:
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', name):
        raise ValueError(f"Invalid CQL identifier: {name!r}")
    return name

# In __init__(): validate before use
self.keyspace = _validate_cql_identifier(self.keyspace)
self.table = _validate_cql_identifier(self.table)
```

![PoC](https://raw.githubusercontent.com/n0z0/cve-evidence/main/2026-04/20260403_004238_glances_cassandra_cql_injection_poc.png)

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-grp3-h8m8-45p7
- https://nvd.nist.gov/vuln/detail/CVE-2026-35588
- https://github.com/nicolargo/glances/commit/d339181f03a14bb15506307e9d58f876e23d8160
- https://github.com/nicolargo/glances/commit/e41b665576f9fd5374e3152078726cc59a01e48c
- https://github.com/nicolargo/glances
