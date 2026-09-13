# [M] OpenProject: Improper Access Control on OpenProject through /projects/[projectName]/meetings via "invited_user_id" in GET parameter "filters" leads to user names disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-44731
Aliases: GHSA-x7j3-cfgf-7mc4
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-44731
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.3.2 and 17.4.0, the web application's meetings filter feature leaks whether a given user ID corresponds to a valid account and discloses the user's full name, allowing an attacker to enumerate all existing user accounts by probing user IDs and observing differences in the server response. This vulnerability is fixed in 17.3.2 and 17.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44731.json
- https://github.com/opf/openproject/security/advisories/GHSA-x7j3-cfgf-7mc4
- https://nvd.nist.gov/vuln/detail/CVE-2026-44731
