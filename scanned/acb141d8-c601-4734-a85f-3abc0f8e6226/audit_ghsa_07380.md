# [C] MantisBT: SOAP API Authentication Bypass with Privilege Escalation to Administrator

## Summary
Severity: Critical
Advisory: GHSA-c2xg-qjqw-2v98
CVE: CVE-2026-47156
CWE: CWE-287, CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-c2xg-qjqw-2v98
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.4

## Details
MantisBT 2.28.3 and earlier contains a critical authentication bypass in the SOAP API's mci_check_login() function. Any user knowing any valid cookie_string can authenticate as any other user (knowing their username), including the administrator, without knowing the target's password.

The vulnerability is exploitable with zero prior access on default MantisBT installations because self-registration is enabled by default ($g_allow_signup = ON). A self-registered user can use their own cookie_string (readable from their browser's MANTIS_STRING_COOKIE cookie after login) to impersonate the administrator via the SOAP API.

The REST API is NOT affected. The REST API's AuthMiddleware derives the username server-side from the API token or session cookie, so the username cannot be spoofed.

The Web UI is NOT affected. The Web UI authenticates via PHP session cookies (PHPSESSID) and validates the MANTIS_STRING_COOKIE against the logged-in user through auth_is_cookie_valid(). The username is derived server-side from the cookie, not supplied by the client.

### Impact
- Full administrator access to the SOAP API from zero prior access (with self-registration enabled, which is the default)
- Read/write all issues including private issues and notes across all projects
- Full data exfiltration of all bug reports, attachments, user accounts (id, name, email), and non-private configuration values via the 71 SOAP operations available
- Destructive operations: delete projects, issues, attachments, tags, categories, and versions
- Data manipulation: create/modify issues, impersonate reporters, manage project structure
- Chains with other vulnerabilities: the SOAP admin access enables exploitation of SOAP vulnerabilities that require administrator privileges

### Patches
- https://github.com/mantisbt/mantisbt/commit/e3571c319b1721b41b0dc4b5b5203cbdcbe0c2ee

### Workarounds
None

### Resources
- https://mantisbt.org/bugs/view.php?id=37121

### Credits
MantisBT would like to thank McCaulay Hudson ([@_McCaulay](https://x.com/_mccaulay)) of [watchTowr](https://labs.watchtowr.com/) for originally identifying and responsibly reporting the issue.

The vulnerability  was subsequently discovered by other researchers, while the team was working on fixing and preparing the release. MantisBT credits them here, in chronological order of their reports: 
- Keitaro Yamazaki (@tyage) 
- Harrison Keating (@voraci0us)
- Chandler Johnson (@chndlrx)
- Bharat Devasani (@bharatdevasani)

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-c2xg-qjqw-2v98
- https://github.com/mantisbt/mantisbt/commit/e3571c319b1721b41b0dc4b5b5203cbdcbe0c2ee
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37121
