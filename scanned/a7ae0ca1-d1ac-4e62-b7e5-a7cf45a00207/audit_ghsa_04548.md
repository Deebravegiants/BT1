# [H] SurrealDB: Arbitrary file read via DEFINE ANALYZER mapper() filter

## Summary
Severity: High
Advisory: GHSA-cc8f-fcx3-gpjr
CWE: CWE-209, CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-cc8f-fcx3-gpjr
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.5

## Details
SurrealDB's full-text search lets you define a text analyzer whose `mapper` filter loads a term-mapping file from disk (`DEFINE ANALYZER ... FILTERS mapper('<path>')`). A database user with the `EDITOR` or `OWNER` role could point that filter at any file the SurrealDB process can read and have its content returned in the query's error message.

File access is meant to be restricted by the `SURREAL_FILE_ALLOWLIST` setting, but an empty allowlist applied no restriction at all — and empty is the default. 

## Impact

The file is read with the privileges of the SurrealDB process, so a database `EDITOR` or `OWNER` user can disclose the contents of any file the process can access. Only the **first line** of the file is returned, except for files with no newlines.

However recovering the process's command line and environment could expose startup root credentials (`--user` / `--pass`) and secret environment variables, escalating a single-database role toward full control of the instance.

The read on the underlying filesystem is bounded by what the SurrealDB process can reach — any file readable by the OS user it runs as — so the impact scales with how the process is run and what is mounted into it.

## Patches

A patch has been included in SurrealDB 3.1.5.

File access is now secure by default. `check_is_path_allowed` denies every path when no `SURREAL_FILE_ALLOWLIST` is configured, so the `mapper` filter cannot open any file unless the operator has explicitly allowed its directory. Analyzer parse errors no longer include the contents of the mapped file, only the line number.

## Workarounds

Users unable to upgrade are advised to consider the following:

- Set `SURREAL_FILE_ALLOWLIST` to a directory that contains only the intended mapping files; this confines the `mapper` filter to that path. On affected versions the allowlist must be non-empty to have any effect.
- Grant the `EDITOR` and `OWNER` database roles only to trusted principals.
- Avoid supplying secrets — including the root credentials — on the command line or through environment variables; prefer mounted files with least-privilege permissions.

## References

- [SurrealQL Documentation — DEFINE ANALYZER](https://surrealdb.com/docs/surrealql/statements/define/analyzer#define-analyzer-statement)
- [SurrealDB Documentation — Capabilities](https://surrealdb.com/docs/surrealdb/security/capabilities)
- Related earlier advisory: [GHSA-2cvj-g5r5-jrrg](https://github.com/surrealdb/surrealdb/security/advisories/GHSA-2cvj-g5r5-jrrg) local file read of 2-column TSV files via analyzers
- https://github.com/surrealdb/surrealdb/pull/5600
- fix(iam): deny filesystem access by default and stop leaking file content in analyzer errors

## Acknowledgements

Thanks to Jan Kahmen ([@kah-ja](https://github.com/kah-ja)) for finding and reporting this issue.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-cc8f-fcx3-gpjr
- https://github.com/surrealdb/surrealdb/pull/5600
- https://github.com/surrealdb/surrealdb
