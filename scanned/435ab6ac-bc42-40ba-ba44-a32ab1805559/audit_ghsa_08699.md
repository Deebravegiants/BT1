# [H] MantisBT has a Private Bugnote Attachment Content Leak via REST API

## Summary
Severity: High
Advisory: GHSA-pw5x-2mf9-3xc8
CVE: CVE-2026-42071
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-pw5x-2mf9-3xc8
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.23.0 <2.28.2

## Details
A missing authorization check in MantisBT's file visibility function allows any authenticated user (REPORTER+) to download attachments on private bugnotes they should not be able to access, via the REST API endpoint GET /api/rest/issues/{id}/files and SOAP API mc_issue_attachment_get endpoint.

### Impact
- REPORTER (access level 25) can view file attachments that were uploaded to private bugnotes by DEVELOPER/MANAGER/ADMIN users
- Private bugnotes are intended for internal developer discussion; their attachments (logs, screenshots, patches) should be equally protected
- The web UI is NOT affected — it filters through bugnote_get_all_visible_bugnotes() first

### Patches
- 029d9d203d9e4ae96b3e59d552fa7395cc1e5071

### Workarounds
None

### Credits
Thanks to the following security researchers for independently discovering and responsibly reporting the issue.
- Vishal Shukla 
- Tristan Madani (@TristanInSec) from Talence Security 
- Tang Cheuk Hei (@siunam321) 

This advisory's contents was largely copied from Tristan's well-written report.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-pw5x-2mf9-3xc8
- https://nvd.nist.gov/vuln/detail/CVE-2026-42071
- https://github.com/mantisbt/mantisbt/commit/029d9d203d9e4ae96b3e59d552fa7395cc1e5071
- https://github.com/advisories/GHSA-xjmx-cprh-646r
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=27039
- https://mantisbt.org/bugs/view.php?id=36985
- https://mantisbt.org/bugs/view.php?id=37092
