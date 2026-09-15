# [C] laravel-jqgrid vulnerable to SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-3fhj-wpvj-x5w8
CVE: CVE-2021-4262
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-19
Source: https://github.com/advisories/GHSA-3fhj-wpvj-x5w8
Type: github-advisory

## Affected
- Packagist: `mgallegos/laravel-jqgrid` — affected >=0

## Details
A vulnerability classified as critical was found in laravel-jqgrid. Affected by this vulnerability is the function getRows of the file src/Mgallegos/LaravelJqgrid/Repositories/EloquentRepositoryAbstract.php. The manipulation leads to sql injection. The name of the patch is fbc2d94f43d0dc772767a5bdb2681133036f935e. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-216271.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4262
- https://github.com/mgallegos/laravel-jqgrid/pull/72
- https://github.com/mgallegos/laravel-jqgrid/commit/fbc2d94f43d0dc772767a5bdb2681133036f935e
- https://github.com/mgallegos/laravel-jqgrid
- https://vuldb.com/?id.216271
