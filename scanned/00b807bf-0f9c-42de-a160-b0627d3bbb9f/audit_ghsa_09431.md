# [M] MantisBT: Authorization Bypass in Bugnote Editing via Issue Update API

## Summary
Severity: Medium
Advisory: GHSA-pq86-j2c2-47f6
CVE: CVE-2026-42070
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-pq86-j2c2-47f6
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.2

## Details
The mc_issue_update() function in MantisBT allows users having *update_bug_threshold* access (UPDATER, with default settings) to edit, change view state, and modify time tracking on bugnotes belonging to other users — bypassing the default DEVELOPER (level 55) threshold required by the dedicated mc_issue_note_update() function.

### Impact
1. UPDATER can edit notes by DEVELOPER/MANAGER/ADMIN — bypassing the DEVELOPER threshold
2. UPDATER can change private notes to public — exposing confidential internal discussion
3. UPDATER can change public notes to private — hiding information from reporters/viewers

### Patches
- 6e58fae4f22efdc3987f903c8ba2611de17a9435

### Workarounds
None

### Credits
Thanks to the following security researchers for independently discovering and responsibly reporting the issue.
- Vishal Shukla 
- Tristan Madani (@TristanInSec) from Talence Security 

This advisory's contents was largely copied from Tristan's well-written report.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-pq86-j2c2-47f6
- https://nvd.nist.gov/vuln/detail/CVE-2026-42070
- https://github.com/mantisbt/mantisbt/commit/6e58fae4f22efdc3987f903c8ba2611de17a9435
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37089
- https://mantisbt.org/bugs/view.php?id=37093
