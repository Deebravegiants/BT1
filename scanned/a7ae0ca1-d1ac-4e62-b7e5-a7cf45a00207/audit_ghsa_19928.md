# [M] Roots Soil plugin vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-jw6x-4h8h-569x
CVE: CVE-2022-4524
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-15
Source: https://github.com/advisories/GHSA-jw6x-4h8h-569x
Type: github-advisory

## Affected
- Packagist: `roots/soil` — affected >=0 <4.1.0

## Details
A vulnerability, which was classified as problematic, was found in Roots soil Plugin up to 4.1.0. Affected is the function language_attributes of the file src/Modules/CleanUpModule.php. The manipulation of the argument language leads to cross site scripting. It is possible to launch the attack remotely. Upgrading to version 4.1.1 is able to address this issue. The name of the patch is 0c9151e00ab047da253e5cdbfccb204dd423269d. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-215904.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4524
- https://github.com/roots/soil/pull/285
- https://github.com/roots/soil/commit/0c9151e00ab047da253e5cdbfccb204dd423269d
- https://github.com/roots/soil
- https://github.com/roots/soil/releases/tag/4.1.0
- https://github.com/roots/soil/releases/tag/4.1.1
- https://vuldb.com/?id.215904
