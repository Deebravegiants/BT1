# [M] MantisBT: REST and SOAP API Issue Update Accepts Unreleased Product Versions From Updaters

## Summary
Severity: Medium
Advisory: GHSA-3v2j-6fw9-f57c
CVE: CVE-2026-52882
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-3v2j-6fw9-f57c
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.4

## Details
### Impact
Users below _report_issues_for_unreleased_versions_threshold_ can assign unreleased product versions.

### Patches
- https://github.com/mantisbt/mantisbt/commit/17072d4c322c85f7135ebec3417a6d90b525d12f

### Workarounds
None

### Resources
- https://mantisbt.org/bugs/view.php?id=37065

### Credits
MantisBT thanks Vishal Shukla for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-3v2j-6fw9-f57c
- https://github.com/mantisbt/mantisbt/commit/17072d4c322c85f7135ebec3417a6d90b525d12f
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37065
