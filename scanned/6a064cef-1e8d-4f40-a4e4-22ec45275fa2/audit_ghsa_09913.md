# [H] Dagster Vulnerable to SQL Injection via Dynamic Partition Keys in Database I/O Manager Integrations

## Summary
Severity: High
Advisory: GHSA-mjw2-v2hm-wj34
CVE: CVE-2026-41490
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-18
Source: https://github.com/advisories/GHSA-mjw2-v2hm-wj34
Type: github-advisory

## Affected
- PyPI: `dagster-duckdb` — affected >=0 <0.29.1
- PyPI: `dagster-snowflake` — affected >=0 <0.29.1
- PyPI: `dagster-gcp` — affected >=0 <0.29.1
- PyPI: `dagster` — affected >=0 <1.13.1
- PyPI: `dagster-deltalake` — affected >=0 <0.29.1
- PyPI: `dagster-snowflake-polars` — affected >=0 <0.29.1

## Details
### Summary

The DuckDB, Snowflake, BigQuery, and DeltaLake I/O managers constructed SQL WHERE clauses by interpolating dynamic partition key values into queries without escaping. A user with the `Add Dynamic Partitions` permission could create a partition key that injects arbitrary SQL, which would execute against the target database backend under the I/O manager's credentials.

Only deployments that use dynamic partitions are affected. Pipelines using static or time-window partitions are not impacted.

### Impact

**Dagster OSS**: Any user with access to the Dagster API can create dynamic partition keys. Organizations should assess exposure based on who has API access in their deployment. Dagster is typically deployed in trusted environments where users who can manage partitions already have equivalent database access through other means. 

**Dagster+**: In most Dagster+ deployments using default permission sets, the `Add Dynamic Partitions` permission is granted to users with an Editor role or above, who typically already have the ability to modify the affected tables and the asset code that accesses them.

The vulnerability is most relevant in deployments where this permission has been granted independently of broader database access, such as certain multi-tenant or custom RBAC configurations. In those cases, an affected user could read or modify data within the databases accessible to the I/O manager, beyond what their role would otherwise permit. Organizations should review which users hold this permission and assess their exposure accordingly.

### Remediation

**Update to the patched versions listed above.** No configuration changes or workarounds are required alongside the update. Only your Dagster code version needs to be updated; the Dagster+ agent/Dagster OSS daemon/webserver do not need to be updated.

The fix ensures that partition key values are properly escaped before inclusion in SQL queries across all affected I/O managers.

If you are unable to apply the update, manual workarounds are described [here](https://gist.github.com/gibsondan/6d0c483f8499a8b1cd460cddc9fd8f72).

## References
- https://github.com/dagster-io/dagster/security/advisories/GHSA-mjw2-v2hm-wj34
- https://nvd.nist.gov/vuln/detail/CVE-2026-41490
- https://gist.github.com/gibsondan/6d0c483f8499a8b1cd460cddc9fd8f72
- https://github.com/dagster-io/dagster
- https://github.com/dagster-io/dagster/releases/tag/1.13.1
