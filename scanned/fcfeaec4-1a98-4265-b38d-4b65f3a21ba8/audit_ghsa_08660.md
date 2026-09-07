# [H] MantisBT is Vulnerable to Stored XSS in Saved-Filter Owner Column

## Summary
Severity: High
Advisory: GHSA-f633-865q-2mhh
CVE: CVE-2026-40607
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-f633-865q-2mhh
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.1.0 <2.28.2

## Details
Incorrect escaping of a saved filter's owner allows an attacker to inject arbitrary HTML on systems where $g_show_user_realname = ON.

### Impact
Cross-site scripting (XSS).

Note that By default, only users with *Manager* access level or above can save their filters publicly

### Patches
- 44f490bcf20fd491c1b8f3fc9dd041d8c2a30010

### Workarounds
- Prevent display of users' real name (set `$g_ show_user_realname = OFF;` in configuration)
- Restrict ability to store filters (set $`g_stored_query_create_threshold` / $`g_stored_query_create_shared_threshold` to `NOBODY` 

### Credits
Thanks to siunam (Tang Cheuk Hei) for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-f633-865q-2mhh
- https://nvd.nist.gov/vuln/detail/CVE-2026-40607
- https://github.com/mantisbt/mantisbt/commit/44f490bcf20fd491c1b8f3fc9dd041d8c2a30010
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37015
