# [M] MantisBT lacks verification when changing a user's email address

## Summary
Severity: Medium
Advisory: GHSA-q747-c74m-69pr
CVE: CVE-2025-55155
CWE: CWE-201, CWE-345
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-11-03
Source: https://github.com/advisories/GHSA-q747-c74m-69pr
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.27.2

## Details
When a user edits their profile to change their e-mail address, the system saves it without validating that it actually belongs to the user.

### Impact
This could result in storing an invalid email address, preventing the user from receiving system notifications.

Notifications sent to another person's email address could lead to information disclosure.

### Patches
Fixed in 2.27.2.

### Workarounds
None

### Credits

Thanks to @ncrcs for discovering and reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-q747-c74m-69pr
- https://nvd.nist.gov/vuln/detail/CVE-2025-55155
- https://github.com/mantisbt/mantisbt/commit/21e9fbedde8553c29c0d3156e84f78157fc4f22e
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=36005
