# [H] Laravel Excel writes exports outside the configured filesystem disk when given a caller-controlled path

## Summary
Severity: High
Advisory: CVE-2026-84374
Aliases: GHSA-c7r6-vx3h-w5g2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84374
Type: osv

## Details
Laravel Excel provides supercharged Excel exports and imports in Laravel. From 3.1.8 until 3.1.70, in src/Files/Disk.php the Maatwebsite\Excel\Files\Disk::copy() method resolves the caller-controlled $destination supplied through Excel::store(), $export->store(), or storeExcel() against the process working directory with realpath() instead of the configured filesystem disk. If the path names an existing writable file, Disk::copy() opens it with fopen() in rb+ mode and uses stream_copy_to_stream(), bypassing Flysystem path confinement and allowing an attacker whose application input controls the export path to overwrite arbitrary existing files with export content. The rb+ behavior creates a non-truncating overwrite and trailing bytes when the new export is shorter, and overwriting an executable PHP file can lead to remote code execution. This issue is fixed in version 3.1.70.

## References
- https://github.com/SpartnerNL/Laravel-Excel/releases/tag/3.1.70
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84374.json
- https://github.com/SpartnerNL/Laravel-Excel/security/advisories/GHSA-c7r6-vx3h-w5g2
- https://nvd.nist.gov/vuln/detail/CVE-2026-84374
- https://github.com/SpartnerNL/Laravel-Excel/commit/b5cafdfcf7ec63924e83303763be8fcae340f70b
