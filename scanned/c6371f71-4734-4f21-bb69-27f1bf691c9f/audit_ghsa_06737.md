# [M] MantisBT: Injection of TIME_TRACKING and REMINDER Notes via REST and SOAP APIs

## Summary
Severity: Medium
Advisory: GHSA-4vpf-w7qv-5h3q
CVE: CVE-2026-52883
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-4vpf-w7qv-5h3q
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.4

## Details
Unvalidated note_type Parameter in mc_issue_update SOAP Endpoint Allows creation of TIME_TRACKING and REMINDER Notes. The SOAP path passes the user-supplied note_type integer directly to bugnote_add() without validating that the user is authorized to create that type of note. If the user's access level is higher than *$g_time_tracking_view_threshold*, they can also inject arbitrary hours into billing reports.

REST API also allows injection of TIME_TRACKING notes (but not REMINDER) through the same mc_issue_update() function.

### Impact
An attacker with UPDATER access could:
- Inject fake billable hours via TIME_TRACKING notes (note_type=2), corrupting billing data exported through MantisBT's billing reports. Organizations that bill clients based on MantisBT time tracking data would generate incorrect invoices, and corrupt time tracking reports could be used to drive project management decisions.
- Fake REMINDER notes registered (but without actual sending of notifications).

### Patches
- https://github.com/mantisbt/mantisbt/commit/de2f71fd88746e963386c214c3ae65a3c4c851b7

### Workarounds
None

### Resources
- https://mantisbt.org/bugs/view.php?id=37081
- https://mantisbt.org/bugs/view.php?id=37200

### Credits
Thanks to the following security researchers for discovering and responsibly reporting the issue
- Vishal Shukla
- Psalms Christopher Matovu (@byteoverride)

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-4vpf-w7qv-5h3q
- https://github.com/mantisbt/mantisbt/commit/de2f71fd88746e963386c214c3ae65a3c4c851b7
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37081
- https://mantisbt.org/bugs/view.php?id=37200
