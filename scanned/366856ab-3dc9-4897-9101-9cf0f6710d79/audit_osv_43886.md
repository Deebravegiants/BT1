# [M] AshAdmin cookie reader matches names by substring, enabling actor/session shadowing from a sibling subdomain

## Summary
Severity: Medium
Advisory: CVE-2026-75757
Aliases: EEF-CVE-2026-75757, GHSA-3259-55fp-w94j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-75757
Type: osv

## Details
Reliance on Cookies without Validation and Integrity Checking vulnerability in ash-project ash_admin lets an attacker who controls a sibling subdomain rebind an admin's session to a different actor, tenant, or authorization mode.

AshAdmin's client JavaScript read its state cookies (tenant, actor_resource, actor_primary_key, actor_action, actor_domain, actor_authorizing, actor_paused) by matching the cookie name with an unanchored regular expression (new RegExp(name + "=([^;]+)")) against the whole document.cookie. Any cookie whose name merely ends with the requested name therefore matches, and whichever is serialized first wins. Because cookies are shared across a registrable domain, a compromised sibling subdomain can set a shadowing cookie (for example xactor_authorizing) with Domain=.example.com that flows unvalidated into the admin's LiveSocket connect params. The fix matches cookie names by exact equality.

This issue affects ash_admin: from 0.9.1 before 1.3.1.

## References
- https://cna.erlef.org/cves/CVE-2026-75757.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-75757
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75757.json
- https://github.com/ash-project/ash_admin/security/advisories/GHSA-3259-55fp-w94j
- https://nvd.nist.gov/vuln/detail/CVE-2026-75757
- https://github.com/ash-project/ash_admin/commit/e93a3408a85035e1f90275d02bc2470c96095e56
- https://github.com/ash-project/ash_admin
