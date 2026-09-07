# [M] MantisBT has an authorization bypass in private issue monitoring

## Summary
Severity: Medium
Advisory: GHSA-ggw7-9675-6v4v
CVE: CVE-2026-34579
CWE: CWE-200, CWE-201
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-ggw7-9675-6v4v
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.26.1 <2.28.2

## Details
Using a crafted POST request to bug_monitor_add.php, a user with project-level access can add themselves as a monitor for a private issue they do not have access to. Despite displaying an Access Denied error, the application accepts the request and creates a monitor relationship for the private issue.


### Impact
Direct access to the private issue remains blocked, but the user will receive email notifications for updates, leading to disclosure of the private issue's metadata and content.

### Patches
- 0a93267deba445fb9d15250c16e6fdb1246ffa65

### Workarounds
None

### Credits
Thanks to Vishal Shukla for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-ggw7-9675-6v4v
- https://nvd.nist.gov/vuln/detail/CVE-2026-34579
- https://github.com/mantisbt/mantisbt/commit/0a93267deba445fb9d15250c16e6fdb1246ffa65
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=36975
