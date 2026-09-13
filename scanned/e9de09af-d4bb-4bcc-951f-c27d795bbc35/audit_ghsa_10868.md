# [M] PowerSync: Some sync filters ignored on 1.20.0 using `config.edition: 3`

## Summary
Severity: Medium
Advisory: GHSA-q6wc-xx4m-92fj
CVE: CVE-2026-30870
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-07
Source: https://github.com/advisories/GHSA-q6wc-xx4m-92fj
Type: github-advisory

## Affected
- npm: `@powersync/service-core` — affected >=1.20.0 <1.20.1
- npm: `@powersync/service-sync-rules` — affected >=0.32.0 <0.33.0

## Details
### Impact

In version **1.20.0**, when using new sync streams with `config.edition: 3`, certain subquery filters were ignored when determining which data to sync to users.

Depending on the sync stream configuration, this could result in authenticated users syncing data that should have been restricted.

Only queries that gate synchronization using subqueries without partitioning the result set are affected.

Not affected:
 * Sync rules (bucket_definitions)
 * Sync streams using `config.edition: 2`
 * No data is exposed without authenticating

### Patches

The issue is **fixed in 1.20.1**. Restarting the service with the new version is sufficient - no reprocessing of sync streams is required.

Any data that users erroneously synced will be automatically removed from those devices when they connect again.

We have updated all affected PowerSync Cloud instances to the fixed version, and are reaching out to affected customers.

For self-hosted PowerSync instances, update to the latest version and restart.

### Affected queries

Subqueries used only to determine whether or not a table should be synced (without partitioning the data itself) are affected. Examples:

```sql
-- Goal: Sync a table only to admin users
-- 1.20.0: all authenticated users would sync this table
SELECT * FROM sensitive_table WHERE auth.user_id() IN (SELECT user_id FROM admins)
SELECT * FROM sensitive_table WHERE 1 IN (SELECT 1 FROM users WHERE id = auth.user_id() AND is_admin = TRUE)

-- Goal: Sync a table only if authorized
-- 1.20.0: all authenticated users would sync this table
SELECT * FROM sensitive_table WHERE 'sensitive_table' IN (SELECT table_name FROM synced_table WHERE "user" = auth.user_id())
SELECT * FROM sensitive_table WHERE 'sensitive_table' IN auth.parameter('allowed_tables')
```

Queries that partition data (for example `SELECT * FROM sensitive_table WHERE owner IN (SELECT id FROM users WHERE is_admin AND id = auth.user_id())`) are not affected by this issue.

## References
- https://github.com/powersync-ja/powersync-service/security/advisories/GHSA-q6wc-xx4m-92fj
- https://nvd.nist.gov/vuln/detail/CVE-2026-30870
- https://github.com/powersync-ja/powersync-service
