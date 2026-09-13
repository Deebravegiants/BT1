# [M] MantisBT: REST API unauthorized Issue status change

## Summary
Severity: Medium
Advisory: GHSA-m7ph-9558-mrx3
CVE: CVE-2026-49280
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-m7ph-9558-mrx3
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.8.0 <2.28.4

## Details
A MantisBT user having *$g_update_bug_threshold* (UPDATER by default) can change an Issue's Status via REST and SOAP API, even if the *$g_set_status_threshold* config is set to a higher level (DEVELOPER by default).

### Impact
Unauthorized change in Issue workflow.

### Patches
https://github.com/mantisbt/mantisbt/releases/tag/release-2.28.4

### Workarounds
None

### Resources
- https://mantisbt.org/bugs/view.php?id=37181

### Credits
Mamdouh Mahfouz (@mamdouhmahfouz)

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-m7ph-9558-mrx3
- https://github.com/mantisbt/mantisbt/commit/2d3a5537605487a1ec5178aba9fe9b5623b6a4e0
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37181
