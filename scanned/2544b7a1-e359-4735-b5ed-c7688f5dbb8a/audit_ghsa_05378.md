# [M] Symfony's incorrect argument escaping under MSYS2/Git Bash can lead to destructive file operations on Windows

## Summary
Severity: Medium
Advisory: GHSA-r39x-jcww-82v6
CVE: CVE-2026-24739
CWE: CWE-88
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-r39x-jcww-82v6
Type: github-advisory

## Affected
- Packagist: `symfony/process` — affected >=0 <5.4.51
- Packagist: `symfony/process` — affected >=6.4 <6.4.33
- Packagist: `symfony/process` — affected >=7.3 <7.3.11
- Packagist: `symfony/process` — affected >=7.4 <7.4.5
- Packagist: `symfony/process` — affected >=8.0 <8.0.5
- Packagist: `symfony/symfony` — affected >=0 <5.4.51
- Packagist: `symfony/symfony` — affected >=6.4 <6.4.33
- Packagist: `symfony/symfony` — affected >=7.3 <7.3.11
- Packagist: `symfony/symfony` — affected >=7.4 <7.4.5
- Packagist: `symfony/symfony` — affected >=8.0 <8.0.5

## Details
### Summary
The Symfony Process component did not correctly treat some characters (notably `=`) as “special” when escaping arguments on Windows. When PHP is executed from an MSYS2-based environment (e.g. Git Bash) and Symfony Process spawns native Windows executables, MSYS2’s argument/path conversion can mishandle unquoted arguments containing these characters.

This can cause the spawned process to receive corrupted/truncated arguments compared to what Symfony intended.

### Impact
If an application (or tooling such as Composer scripts) uses Symfony Process to invoke file-management commands (e.g. `rmdir`, `del`, etc.) with a path argument containing `=`, the MSYS2 conversion layer may alter the argument at runtime. In affected setups this can result in operations being performed on an unintended path, up to and including deletion of the contents of a broader directory or drive.

The issue is particularly relevant when untrusted input can influence process arguments (directly or indirectly, e.g. via repository paths, extracted archive paths, temporary directories, or user-controlled configuration).

### Resolution
Upgrade to a Symfony release that includes the fix from symfony/symfony#63164 (which updates Windows argument escaping to ensure arguments containing = and other MSYS2-sensitive characters are properly quoted/escaped).
The patch for branch 5.4 is available at https://github.com/symfony/symfony/commit/ec154f6f95f8c60f831998ec4d246a857e9d179b

### Workarounds / Mitigations
Avoid running PHP/your tooling from MSYS2-based shells on Windows; prefer cmd.exe or PowerShell for workflows that spawn native executables.
Avoid passing paths containing `=` (and similar MSYS2-sensitive characters) to Symfony Process when operating under Git Bash/MSYS2.
Where applicable, configure MSYS2 to disable or restrict argument conversion (e.g. via `MSYS2_ARG_CONV_EXCL`), understanding this may affect other tooling behavior.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-r39x-jcww-82v6
- https://nvd.nist.gov/vuln/detail/CVE-2026-24739
- https://github.com/symfony/symfony/issues/62921
- https://github.com/symfony/symfony/pull/63164
- https://github.com/symfony/symfony/commit/35203939050e5abd3caf2202113b00cab5d379b3
- https://github.com/symfony/symfony/commit/ec154f6f95f8c60f831998ec4d246a857e9d179b
- https://github.com/symfony/symfony
