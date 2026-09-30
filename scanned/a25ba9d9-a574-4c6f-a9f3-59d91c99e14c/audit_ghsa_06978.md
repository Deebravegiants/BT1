# [H] laravel-backup-restore has an OS Command Injection during database restore

## Summary
Severity: High
Advisory: GHSA-w9mx-xmg4-gc4r
CVE: CVE-2026-53932
CWE: CWE-77, CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-w9mx-xmg4-gc4r
Type: github-advisory

## Affected
- Packagist: `wnx/laravel-backup-restore` — affected >=0 <1.9.4

## Details
## Summary
A crafted backup archive can trigger OS command injection during database restore. The restore workflow extracts a ZIP archive, enumerates files under `db-dumps`, converts the dump path to an absolute path, and passes that path into database import commands that are built as shell command strings.

The dump filename is not shell-escaped before it is interpolated into commands such as:

- `mysql ... < {dumpFile}`
- `gunzip -c {dumpFile}` / `gunzip < {dumpFile}`
- `psql ... < {dumpFile}`
- `sqlite3 ... < {dumpFile}`

Because `Illuminate\Support\Facades\Process::run(string)` uses Symfony `Process::fromShellCommandline()`, shell metacharacters in the dump filename are interpreted by `/bin/sh` on Unix-like systems or by the platform shell on Windows.

### Impact
If an attacker can cause an operator or automation to restore a malicious backup archive, the attacker can execute arbitrary shell commands as the PHP/Laravel application user on the system performing the restore. This can lead to application compromise, database credential disclosure, tampering with restored data, and further lateral movement depending on deployment permissions.

This is not about malicious SQL inside the dump. The command injection is carried in the ZIP entry filename under `db-dumps`, before the dump content is imported.

### Patches
The vulnerability has been fixed in v1.9.4 of the package.

### Workarounds
There is no configuration option that disables the vulnerable code path. Upgrading to the patched release is the only complete fix.

## References
- https://github.com/stefanzweifel/laravel-backup-restore/security/advisories/GHSA-w9mx-xmg4-gc4r
- https://github.com/stefanzweifel/laravel-backup-restore
