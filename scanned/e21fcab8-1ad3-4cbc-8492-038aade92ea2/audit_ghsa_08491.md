# [M] MantisBT is Vulnerable to Stored XSS in Custom Field Textarea Values

## Summary
Severity: Medium
Advisory: GHSA-qj6w-v29q-4rgx
CVE: CVE-2026-39960
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-qj6w-v29q-4rgx
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.2

## Details
Improper escaping of a textarea custom field's contents in the Update Issue page (bug_update_page.php) allows an attacker to inject HTML and, if CSP settings permit, execute arbitrary JavaScript when the page is loaded.

### Impact
Session theft leading to admin account takeover, full project data access.

- Precondition: A textarea-type custom field must be configured for the project
- Attacker: Authenticated user with bug report permission (low privilege)
- Victim: Any user viewing the bug edit form, including administrators

### Patches
- 5fec0f448b7a7d7d539a6adb6dccceac4e4e4ab7

### Workarounds
The default Content-Security Policy will block script execution.

### References
- https://mantisbt.org/bugs/view.php?id=37003
- This is related to [CVE-2024-34081](https://github.com/advisories/GHSA-wgx7-jp56-65mq).

### Credits
Thanks to the following security researchers for independently discovering and responsibly reporting the issue, and providing a patch to fix it.
- Thanks to Nozomu Sasaki (Paul) (@morimori-dev)
- Tristan Madani (@TristanInSec) from Talence Security

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-qj6w-v29q-4rgx
- https://nvd.nist.gov/vuln/detail/CVE-2026-39960
- https://github.com/mantisbt/mantisbt/commit/5fec0f448b7a7d7d539a6adb6dccceac4e4e4ab7
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37003
