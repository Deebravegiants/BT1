# [M] Mantis Bug Tracker (MantisBT) vulnerable to cross-site scripting 

## Summary
Severity: Medium
Advisory: GHSA-wgx7-jp56-65mq
CVE: CVE-2024-34081
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-05-13
Source: https://github.com/advisories/GHSA-wgx7-jp56-65mq
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.26.2

## Details
Improper escaping of a custom field's name allows an attacker to inject HTML and, if CSP settings permit, achieve execution of arbitrary JavaScript when:
- resolving or closing issues (bug_change_status_page.php) belonging to a project linking said custom field
- viewing issues (view_all_bug_page.php) when the custom field is displayed as a column
- printing issues (print_all_bug_page.php) when the custom field is displayed as a column

### Impact
Cross-site scripting (XSS).

### Patches
https://github.com/mantisbt/mantisbt/commit/447a521aae0f82f791b8116a14a20e276df739be

### Workarounds
Ensure Custom Field Names do not contain HTML tags.

### References
- https://mantisbt.org/bugs/view.php?id=34432
- This is related to CVE-2020-25830 (same root cause, different affected pages)

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-wgx7-jp56-65mq
- https://nvd.nist.gov/vuln/detail/CVE-2024-34081
- https://github.com/mantisbt/mantisbt/commit/447a521aae0f82f791b8116a14a20e276df739be
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=34432
