# [M] NocoBase backup restore schema name allows command injection

## Summary
Severity: Medium
Advisory: GHSA-p853-83gj-wjj3
CVE: CVE-2026-55410
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-p853-83gj-wjj3
Type: github-advisory

## Affected
- npm: `@nocobase/plugin-backups` — affected >=0 <2.1.19

## Details
### Summary
NocoBase `@nocobase/plugin-backups` 2.0.57 restores PostgreSQL backups by interpolating the backup metadata schema name into shell command strings that are executed with Node.js `child_process.exec()`. A backup-management user who can restore an uploaded PostgreSQL backup with forced schema restore can place shell metacharacters in `_metadata.json` under `database.schema`, causing arbitrary commands to execute as the NocoBase server process during restore.

The vulnerable plugin is included in the default `@nocobase/preset-nocobase` package and is guarded by the backup-management ACL snippet (`backups:*` / `backup:*`). This is not unauthenticated; the attacker must have backup restore privileges or equivalent access to the restore API/CLI.

### Details
Affected product evidence:
- Ecosystem/package: npm package `@nocobase/plugin-backups` from `packages/plugins/@nocobase/plugin-backups/package.json`.
- Tested vulnerable version: `2.0.57` (`packages/plugins/@nocobase/plugin-backups/package.json:1-16`).
- Tested commit: `e03d267362b3426f484c28783020b4a2a08911e8`.
- Default/common inclusion: `@nocobase/preset-nocobase` depends on and lists `@nocobase/plugin-backups` 2.0.57 as built in (`packages/presets/nocobase/package.json:22-24`, `packages/presets/nocobase/package.json:115-128`).
- Affected range estimate: at least the tested `2.0.57` checkout. Earlier/later versions were not tested.
- Patched version: unknown/not available in this local checkout.

Source-to-sink path:
- The plugin registers backup-management snippets for `backups:*` and `backup:*`, so the restore API is intended for roles granted backup-management permissions (`packages/plugins/@nocobase/plugin-backups/src/server/plugin.ts:51-59`).
- The `backup` restore-upload action accepts request body/query `force` and passes it as `forceSchemaRestore` to `RestoreManager.restore()` (`packages/plugins/@nocobase/plugin-backups/src/server/resourcers/backup-cli.ts:40-42`, `packages/plugins/@nocobase/plugin-backups/src/server/resourcers/backup-cli.ts:200-211`).
- `RestoreManager` decompresses the uploaded backup archive, reads `_metadata.json`, and parses attacker-controlled JSON metadata (`packages/plugins/@nocobase/plugin-backups/src/server/managers/restore.ts:203-215`, `packages/plugins/@nocobase/plugin-backups/src/server/managers/restore.ts:257-267`).
- When `forceSchemaRestore` is true and the database dialect is PostgreSQL, the schema-mismatch check is skipped (`packages/plugins/@nocobase/plugin-backups/src/server/managers/restore.ts:270-300`). Existing tests confirm forced schema restore intentionally allows a metadata schema mismatch (`packages/plugins/@nocobase/plugin-backups/src/server/__tests__/managers/restore.test.ts:336-356`) and that the API passes `forceSchemaRestore: true` when `force=true` is supplied (`packages/plugins/@nocobase/plugin-backups/src/server/__tests__/managers/restore.test.ts:377-409`).
- The parsed `metadata.database.schema` is passed into `this.#dbAdapter.restore(path.join(extractedDir, dbFile), metadata.database.schema)` (`packages/plugins/@nocobase/plugin-backups/src/server/managers/restore.ts:427-448`).
- For PostgreSQL, if the backup schema differs from the target schema, `PostgresAdapter.restore()` assigns `srcSchema = schema || 'public'` and builds `pgRestoreCommand` using `-n ${srcSchema}` with no quoting or argument array (`packages/plugins/@nocobase/plugin-backups/src/server/adapters/database.ts:350-420`).
- `#restoreSchema()` also interpolates `srcSchema` and `targetSchema` directly into SQL strings and then calls `run(pgRestoreCommand, ...)` (`packages/plugins/@nocobase/plugin-backups/src/server/adapters/database.ts:423-451`).
- `run()` executes the assembled string through `child_process.exec()`, which invokes a shell (`packages/plugins/@nocobase/plugin-backups/src/server/adapters/database.ts:1-31`).

A schema value such as `safe; touch /tmp/nocobase-cve-marker #` produces a restore command of this form:

```text
pg_restore -U u -h localhost -p 5432 -n safe; touch /tmp/nocobase-cve-marker # -d db --clean --if-exists --no-owner -j 1 /tmp/backup-data
```

The semicolon terminates the intended `pg_restore` command and starts a new shell command.

False-positive screening:
- This report does not claim unauthenticated exploitation. The route is gated by backup-management permissions through the registered ACL snippet.
- The older `backups.upload` resource path was reviewed and does not pass `forceSchemaRestore`; the directly confirmed force path is the `backup.restoreUpload` / backup-CLI API path (`packages/plugins/@nocobase/plugin-backups/src/server/resourcers/backups.ts:54-77`, `packages/plugins/@nocobase/plugin-backups/src/server/resourcers/backup-cli.ts:200-211`).
- The schema mismatch check blocks mismatched metadata by default, but it is deliberately bypassed for PostgreSQL when the supported force option is true.
- The command injection is in the shell command itself before any PostgreSQL connection or valid backup file is required; the safe PoC proves shell metacharacter execution locally without connecting to a database.
- The finding is not based on existing reports or generated writeups.

### PoC
The following local-only PoC renders the same vulnerable `pg_restore` command shape built by `PostgresAdapter.restore()` and executes it through Node.js `child_process.exec()`, the sink used by the plugin. It uses a harmless marker file under `/tmp`, does not contact external services, and cleans up after itself.

From a clean checkout of the tested commit:

```bash
cd nocobase
rm -f /tmp/nocobase-cve-marker
node - <<'NODE'
const { exec } = require('child_process');

const schemaFromBackupMetadata = 'safe; touch /tmp/nocobase-cve-marker #';
const command = `pg_restore -U u -h localhost -p 5432 -n ${schemaFromBackupMetadata} -d db --clean --if-exists --no-owner -j 1 /tmp/backup-data`;

exec(command, () => {
  const fs = require('fs');
  console.log(fs.existsSync('/tmp/nocobase-cve-marker') ? 'marker-created' : 'marker-missing');
  fs.rmSync('/tmp/nocobase-cve-marker', { force: true });
});
NODE
```

Observed output in this environment:

```text
marker-created
```

Expected vulnerable output: `marker-created`, proving the schema value starts a second shell command.

Negative/control case: replace `schemaFromBackupMetadata` with `safe_schema`; the same harness should print `marker-missing` because no shell metacharacter starts the `touch` command.

Maintainer-runnable application-level trigger:
1. Run NocoBase 2.0.57 with PostgreSQL and the built-in `@nocobase/plugin-backups` enabled.
2. Use a role granted the backup-management snippet/actions (`backups:*` / `backup:*`).
3. Create a NocoBase backup archive containing a `data` member and `_metadata.json` with matching dialect/table settings but `database.schema` set to `safe; touch /tmp/nocobase-cve-marker #`.
4. Restore the uploaded backup through the `backup` restore-upload path with `force=true` so PostgreSQL schema mismatch is allowed.
5. Vulnerable behavior: `/tmp/nocobase-cve-marker` exists on the server after restore begins, even if `pg_restore` or database connection later fails.
6. Cleanup: remove `/tmp/nocobase-cve-marker` and discard the test database/container.

### Impact
A user with backup restore privileges can execute arbitrary shell commands as the NocoBase server OS user. In a typical server or container deployment, this can read application configuration and environment secrets, modify application files or database backups, run network clients from the server, and disrupt service availability.

The required application privilege is high because backup restore is an administrative operation. However, backup-management permission is still an application-level role boundary; it should not imply arbitrary operating-system command execution.

### Suggested remediation
Do not execute database tools through shell-interpreted command strings. Use `spawn()` or `execFile()` with an argument array for `pg_restore`, `psql`, `pg_dump`, `mysql`, and related tools. Validate PostgreSQL schema identifiers from backup metadata against PostgreSQL identifier rules or quote them using the database driver's identifier-quoting facilities before using them in SQL.

For this specific path:
- Pass `pg_restore` arguments as an array, for example `['-U', username, '-h', host, '-p', String(port), '-n', srcSchema, '-d', database, ...]`.
- Reject schema names containing shell metacharacters, quotes, whitespace, comments, or characters outside accepted PostgreSQL identifier syntax unless they are safely handled as identifiers.
- Replace dynamic SQL string interpolation in `#restoreSchema()` with identifier-safe quoting (`format('%I', ...)` in PostgreSQL or equivalent server-side parameters) and string-literal escaping where literals are required.
- Add regression tests that restore a backup whose metadata schema contains `; touch /tmp/should-not-exist #` and assert no marker file is created and the request is rejected.

## References
- https://github.com/nocobase/nocobase/security/advisories/GHSA-p853-83gj-wjj3
- https://nvd.nist.gov/vuln/detail/CVE-2026-55410
- https://github.com/nocobase/nocobase/commit/0e1aba1b7b112ffc841588963f7343c00edd9806
- https://github.com/nocobase/nocobase
- https://github.com/nocobase/nocobase/releases/tag/v2.1.19
