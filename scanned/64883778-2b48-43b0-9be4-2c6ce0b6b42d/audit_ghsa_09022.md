# [H] MantisBT is Vulnerable to Stored HTML Injection/XSS in Clone Issue Form

## Summary
Severity: High
Advisory: GHSA-fvjf-68wh-rwp2
CVE: CVE-2026-34463
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-fvjf-68wh-rwp2
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.2

## Details
When cloning an issue originating from a Project other than the current one, the clone form (bug_report_page.php) prepends the source Project name before the category selector without proper escaping, allowing an attacker able to to inject HTML if they can set the Project's name (which typically requires *manager* or *administrator* access level).


### Impact
Cross-site scripting (XSS).
This is mitigated by Content Security Policy which restricts scripts execution.

### Patches
- df22697ae497ddd93f3d9132fdf4979db8d081cd

### Workarounds
Make sure Project names do not contain any HTML tags.

### Credits
Thanks to Vishal Shukla for discovering and responsibly reporting the issue.

The vulnerability was also identified and independently reported by @siunam321 (Tang Cheuk Hei), prior to this Advisory's publication.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-fvjf-68wh-rwp2
- https://nvd.nist.gov/vuln/detail/CVE-2026-34463
- https://github.com/mantisbt/mantisbt/commit/df22697ae497ddd93f3d9132fdf4979db8d081cd
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=36986
